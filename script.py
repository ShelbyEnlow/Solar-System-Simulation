import math
import tkinter as tk
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx
import numpy as np
from diskcache import Cache
from PIL import Image, ImageTk
from pydantic import BaseModel


BODY_IDS = {
    "Sun": "10",
    "Mercury": "199",
    "Venus": "299",
    "Earth": "399",
    "Mars": "499",
    "Jupiter": "599",
    "Saturn": "699",
    "Uranus": "799",
    "Neptune": "899",
}

MOON_IDS_BY_PLANET = {
    "Earth": {"Moon": "301"},
    "Mars": {"Phobos": "401", "Deimos": "402"},
    "Jupiter": {"Io": "501", "Europa": "502", "Ganymede": "503", "Callisto": "504"},
    "Saturn": {"Mimas": "601", "Rhea": "605", "Titan": "606", "Iapetus": "608"},
    "Uranus": {"Miranda": "705", "Ariel": "701", "Umbriel": "702", "Titania": "703", "Oberon": "704"},
    "Neptune": {"Triton": "801", "Nereid": "802"},
}

BODY_MASS_KG = {
    "Sun": 1.98847e30,
    "Mercury": 3.3011e23,
    "Venus": 4.8675e24,
    "Earth": 5.97219e24,
    "Mars": 6.4171e23,
    "Jupiter": 1.89813e27,
    "Saturn": 5.6834e26,
    "Uranus": 8.6810e25,
    "Neptune": 1.02413e26,
}

MOON_MASS_KG = {
    "Moon": 7.342e22,
    "Phobos": 1.0659e16,
    "Deimos": 1.4762e15,
    "Io": 8.9319e22,
    "Europa": 4.7998e22,
    "Ganymede": 1.4819e23,
    "Callisto": 1.0759e23,
    "Mimas": 3.7493e19,
    "Rhea": 2.3065e21,
    "Titan": 1.3452e23,
    "Iapetus": 1.8056e21,
    "Miranda": 6.59e19,
    "Ariel": 1.353e21,
    "Umbriel": 1.172e21,
    "Titania": 3.527e21,
    "Oberon": 3.014e21,
    "Triton": 2.139e22,
    "Nereid": 3.1e19,
}

MOON_RADIUS_KM = {
    "Moon": 1737.4,
    "Phobos": 11.267,
    "Deimos": 6.2,
    "Io": 1821.6,
    "Europa": 1560.8,
    "Ganymede": 2634.1,
    "Callisto": 2410.3,
    "Mimas": 198.2,
    "Rhea": 763.8,
    "Titan": 2574.7,
    "Iapetus": 734.5,
    "Miranda": 235.8,
    "Ariel": 578.9,
    "Umbriel": 584.7,
    "Titania": 788.9,
    "Oberon": 761.4,
    "Triton": 1353.4,
    "Nereid": 170.0,
}

MOON_COLORS = {
    "Moon": "#c8c8c8",
    "Phobos": "#8e7f72",
    "Deimos": "#9a8d82",
    "Io": "#e0cf78",
    "Europa": "#ddd5be",
    "Ganymede": "#bca890",
    "Callisto": "#8f7e6c",
    "Mimas": "#bdb8b2",
    "Rhea": "#c7c1b8",
    "Titan": "#d6a86e",
    "Iapetus": "#a99b8b",
    "Miranda": "#beb7ad",
    "Ariel": "#c9c3b8",
    "Umbriel": "#9f9a92",
    "Titania": "#b4aea4",
    "Oberon": "#9d978e",
    "Triton": "#c8cdd2",
    "Nereid": "#b2b9c0",
}

BODY_COLORS = {
    "Sun": "#f5d142",
    "Mercury": "#9ea2a8",
    "Venus": "#d7b57d",
    "Earth": "#4f83ff",
    "Mars": "#b95b3c",
    "Jupiter": "#c9ae8b",
    "Saturn": "#d7c48f",
    "Uranus": "#8dd8e9",
    "Neptune": "#4c6fd6",
}

BODY_RADIUS_KM = {
    "Sun": 695700.0,
    "Mercury": 2439.7,
    "Venus": 6051.8,
    "Earth": 6371.0,
    "Mars": 3389.5,
    "Jupiter": 69911.0,
    "Saturn": 58232.0,
    "Uranus": 25362.0,
    "Neptune": 24622.0,
}

# Approximate obliquity (deg) used for axis/equator overlay orientation.
BODY_AXIS_TILT_DEG = {
    "Sun": 7.25,
    "Mercury": 0.03,
    "Venus": 177.36,
    "Earth": 23.44,
    "Mars": 25.19,
    "Jupiter": 3.13,
    "Saturn": 26.73,
    "Uranus": 97.77,
    "Neptune": 28.32,
}

AU_KM = 149_597_870.7
SECONDS_PER_DAY = 86_400.0
HORIZONS_URL = "https://ssd.jpl.nasa.gov/api/horizons.api"
MU_ROUTH = 0.5 * (1.0 - math.sqrt(23.0 / 27.0))


class StateVector(BaseModel):
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float


class HorizonsResponse(BaseModel):
    result: str


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    c = color.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


class HorizonsClient:
    def __init__(self, cache_dir: Path) -> None:
        self.cache = Cache(str(cache_dir))
        self.client = httpx.Client(timeout=20.0)

    def close(self) -> None:
        self.client.close()
        self.cache.close()

    @staticmethod
    def _parse_first_state(result_text: str) -> StateVector:
        in_data = False
        for line in result_text.splitlines():
            stripped = line.strip()
            if stripped == "$$SOE":
                in_data = True
                continue
            if stripped == "$$EOE":
                break
            if in_data and stripped:
                parts = [part.strip() for part in line.split(",")]
                return StateVector(
                    x=float(parts[2]),
                    y=float(parts[3]),
                    z=float(parts[4]),
                    vx=float(parts[5]),
                    vy=float(parts[6]),
                    vz=float(parts[7]),
                )
        raise ValueError("No state-vector data found in Horizons response.")

    def fetch_body_state(self, body_id: str, epoch_utc: datetime) -> StateVector:
        time_str = epoch_utc.strftime("%Y-%m-%d %H:%M")
        cache_key = f"{body_id}:{time_str}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return StateVector.model_validate(cached)

        stop_str = (epoch_utc + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M")
        params = {
            "format": "json",
            "COMMAND": f"'{body_id}'",
            "EPHEM_TYPE": "'VECTORS'",
            "CENTER": "'500@0'",
            "START_TIME": f"'{time_str}'",
            "STOP_TIME": f"'{stop_str}'",
            "STEP_SIZE": "'1 m'",
            "OUT_UNITS": "'AU-D'",
            "VEC_TABLE": "'2'",
            "CSV_FORMAT": "'YES'",
        }
        response = self.client.get(HORIZONS_URL, params=params)
        response.raise_for_status()
        payload = HorizonsResponse.model_validate(response.json())
        state = self._parse_first_state(payload.result)
        self.cache.set(cache_key, state.model_dump(), expire=60 * 60 * 24)
        return state


def fetch_all_body_states_au_once() -> tuple[
    datetime, dict[str, StateVector], dict[str, dict[str, StateVector]]
]:
    epoch = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    client = HorizonsClient(Path(".cache") / "horizons")
    try:
        body_states = {
            name: client.fetch_body_state(body_id, epoch) for name, body_id in BODY_IDS.items()
        }
        moon_states: dict[str, dict[str, StateVector]] = {}
        for planet, moons in MOON_IDS_BY_PLANET.items():
            moon_states[planet] = {}
            for moon_name, moon_id in moons.items():
                try:
                    moon_states[planet][moon_name] = client.fetch_body_state(moon_id, epoch)
                except Exception:
                    # Skip unavailable moon entries without breaking the whole scene.
                    continue
    finally:
        client.close()
    return epoch, body_states, moon_states


class Solar3DViewer:
    def __init__(
        self,
        epoch: datetime,
        relative_positions: dict[str, np.ndarray],
        relative_velocities: dict[str, np.ndarray],
        moon_positions_by_parent: dict[str, dict[str, np.ndarray]],
        moon_velocities_by_parent: dict[str, dict[str, np.ndarray]],
    ) -> None:
        self.epoch = epoch
        self.relative_positions = relative_positions
        self.relative_velocities = relative_velocities
        self.moon_positions_by_parent = moon_positions_by_parent
        self.moon_velocities_by_parent = moon_velocities_by_parent

        self.root = tk.Tk()
        self.root.title("Solar System 3D (JPL Horizons)")
        self.root.geometry("1400x1000")
        self.root.configure(bg="black")

        self.canvas = tk.Canvas(self.root, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        max_radius = max(float(np.linalg.norm(v)) for v in relative_positions.values())
        self.scene_radius = max(max_radius, 1e-8)

        self.yaw = math.radians(35.0)
        self.pitch = math.radians(20.0)
        self.camera_distance = self.scene_radius * 2.6
        self.camera_focus = np.array([0.0, 0.0, 0.0], dtype=np.float64)
        self.focal_factor = 0.95

        self.drag_last: tuple[int, int] | None = None
        self.pan_last: tuple[int, int] | None = None
        self.selected_body = "Sun"
        self.locked_body: str | None = "Sun"
        self.show_lagrange = False
        self.show_belts = False
        self.show_orbits = False
        self.show_moons = False
        self.lagrange_primary = "Sun"
        self.lagrange_secondary = "Earth"
        self.body_order = list(BODY_IDS.keys())
        self.main_belt_points = self._generate_belt_points(
            count=1400, a_min=2.1, a_max=3.3, e_mean=0.12, e_sigma=0.08, i_sigma_deg=7.0, seed=42
        )
        self.kuiper_belt_points = self._generate_belt_points(
            count=2200, a_min=30.0, a_max=50.0, e_mean=0.16, e_sigma=0.10, i_sigma_deg=10.0, seed=84
        )

        self.last_screen_positions: dict[str, tuple[float, float, float]] = {}
        self.last_moon_screen_positions: dict[str, tuple[float, float, float]] = {}
        self.last_lagrange_screen_positions: dict[str, tuple[float, float, float]] = {}
        self.selected_lagrange_label: str | None = None
        self.selected_moon_name: str | None = None
        self.info_panel_rect: tuple[float, float, float, float] | None = None
        self.resize_handle_center: tuple[float, float] | None = None
        self.resize_handle_radius = 5.0
        self.resizing_info_panel = False
        self.resize_drag_start_canvas: tuple[int, int] | None = None
        self.info_panel_start_size: tuple[int, int] | None = None
        self.info_panel_width = 540
        self.info_panel_height = 300
        self.left_press_pos: tuple[int, int] | None = None
        self.skip_next_left_release_click = False
        self.sprite_cache: dict[tuple[str, int], ImageTk.PhotoImage] = {}
        self.tk_images: list[ImageTk.PhotoImage] = []

        self.canvas.bind("<ButtonPress-3>", self._on_right_press)
        self.canvas.bind("<ButtonRelease-3>", self._on_right_release)
        self.canvas.bind("<B3-Motion>", self._on_right_drag)
        self.canvas.bind("<ButtonPress-2>", self._on_middle_press)
        self.canvas.bind("<ButtonRelease-2>", self._on_middle_release)
        self.canvas.bind("<B2-Motion>", self._on_middle_drag)
        self.canvas.bind("<ButtonPress-1>", self._on_left_press)
        self.canvas.bind("<B1-Motion>", self._on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_left_release)
        self.canvas.bind("<Double-Button-1>", self._on_left_double_click)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Configure>", self._on_resize)
        self.root.bind("<e>", self._on_lock_earth)
        self.root.bind("<E>", self._on_lock_earth)
        self.root.bind("<s>", self._on_lock_sun)
        self.root.bind("<S>", self._on_lock_sun)
        self.root.bind("<Escape>", self._on_unlock)
        self.root.bind("<l>", self._on_toggle_lagrange)
        self.root.bind("<L>", self._on_toggle_lagrange)
        self.root.bind("<o>", self._on_cycle_lagrange_primary)
        self.root.bind("<O>", self._on_cycle_lagrange_primary)
        self.root.bind("<p>", self._on_cycle_lagrange_secondary)
        self.root.bind("<P>", self._on_cycle_lagrange_secondary)
        self.root.bind("<b>", self._on_toggle_belts)
        self.root.bind("<B>", self._on_toggle_belts)
        self.root.bind("<r>", self._on_toggle_orbits)
        self.root.bind("<R>", self._on_toggle_orbits)
        self.root.bind("<m>", self._on_toggle_moons)
        self.root.bind("<M>", self._on_toggle_moons)

        self._render()

    @staticmethod
    def _moon_token(parent: str, moon: str) -> str:
        return f"moon::{parent}::{moon}"

    @staticmethod
    def _parse_moon_token(token: str) -> tuple[str, str] | None:
        if not token.startswith("moon::"):
            return None
        parts = token.split("::", 2)
        if len(parts) != 3:
            return None
        return parts[1], parts[2]

    def _target_label(self, target: str) -> str:
        moon = self._parse_moon_token(target)
        if moon is None:
            return target
        parent, moon_name = moon
        return f"{moon_name} ({parent})"

    def _resolve_target_state(self, target: str) -> tuple[np.ndarray, np.ndarray, float] | None:
        if target in self.relative_positions:
            mass = BODY_MASS_KG.get(target)
            if mass is None:
                return None
            return self.relative_positions[target], self.relative_velocities[target], mass

        moon = self._parse_moon_token(target)
        if moon is None:
            return None
        parent, moon_name = moon
        pos = self.moon_positions_by_parent.get(parent, {}).get(moon_name)
        vel = self.moon_velocities_by_parent.get(parent, {}).get(moon_name)
        mass = MOON_MASS_KG.get(moon_name)
        if pos is None or vel is None or mass is None:
            return None
        return pos, vel, mass

    def _secondary_candidates(self) -> list[str]:
        candidates = [body for body in self.body_order if body != self.lagrange_primary]
        if self.show_lagrange and self.locked_body in MOON_IDS_BY_PLANET:
            parent = self.locked_body
            for moon_name in self.moon_positions_by_parent.get(parent, {}).keys():
                candidates.append(self._moon_token(parent, moon_name))
        return candidates

    def _current_focus(self) -> np.ndarray:
        if self.locked_body is not None:
            return self.relative_positions[self.locked_body]
        return self.camera_focus

    def _camera_position(self) -> np.ndarray:
        cos_pitch = math.cos(self.pitch)
        offset = np.array(
            [
                self.camera_distance * cos_pitch * math.cos(self.yaw),
                self.camera_distance * math.sin(self.pitch),
                self.camera_distance * cos_pitch * math.sin(self.yaw),
            ],
            dtype=np.float64,
        )
        return self._current_focus() + offset

    def _camera_basis(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        cam = self._camera_position()
        target = self._current_focus()
        world_up = np.array([0.0, 1.0, 0.0], dtype=np.float64)

        forward = target - cam
        forward = forward / np.linalg.norm(forward)

        right = np.cross(world_up, forward)
        right_norm = np.linalg.norm(right)
        if right_norm < 1e-9:
            right = np.array([1.0, 0.0, 0.0], dtype=np.float64)
        else:
            right = right / right_norm
        up = np.cross(forward, right)
        return right, up, forward

    def _project_point(
        self, point: np.ndarray, width: int, height: int
    ) -> tuple[float, float, float] | None:
        cam = self._camera_position()
        right, up, forward = self._camera_basis()
        rel = point - cam
        x_cam = float(np.dot(rel, right))
        y_cam = float(np.dot(rel, up))
        z_cam = float(np.dot(rel, forward))
        if z_cam <= 1e-7:
            return None

        focal_px = min(width, height) * self.focal_factor
        sx = (width / 2.0) + (x_cam / z_cam) * focal_px
        sy = (height / 2.0) - (y_cam / z_cam) * focal_px
        return sx, sy, z_cam

    def _body_draw_radius(self, name: str) -> float:
        proj = self.last_screen_positions.get(name)
        if proj is None:
            return 0.0
        depth = proj[2]
        if depth <= 1e-9:
            return 0.0
        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        focal_px = min(width, height) * self.focal_factor
        body_radius_au = BODY_RADIUS_KM[name] / AU_KM
        projected = (body_radius_au / depth) * focal_px
        min_visible = 1.6 if name == "Sun" else 1.0
        return max(projected, min_visible)

    @staticmethod
    def _generate_belt_points(
        count: int,
        a_min: float,
        a_max: float,
        e_mean: float,
        e_sigma: float,
        i_sigma_deg: float,
        seed: int,
    ) -> np.ndarray:
        rng = np.random.default_rng(seed)
        a = rng.uniform(a_min, a_max, count)
        e = np.clip(rng.normal(e_mean, e_sigma, count), 0.0, 0.45)
        f = rng.uniform(0.0, 2.0 * math.pi, count)
        omega = rng.uniform(0.0, 2.0 * math.pi, count)
        node = rng.uniform(0.0, 2.0 * math.pi, count)
        inc = rng.normal(0.0, math.radians(i_sigma_deg), count)

        r = a * (1.0 - e * e) / (1.0 + e * np.cos(f))
        u = omega + f
        cos_u = np.cos(u)
        sin_u = np.sin(u)
        cos_o = np.cos(node)
        sin_o = np.sin(node)
        cos_i = np.cos(inc)
        sin_i = np.sin(inc)

        x = r * (cos_o * cos_u - sin_o * sin_u * cos_i)
        y = r * (sin_o * cos_u + cos_o * sin_u * cos_i)
        z = r * (sin_u * sin_i)
        return np.column_stack((x, y, z)).astype(np.float64)

    @staticmethod
    def _body_variation(name: str, nx: np.ndarray, ny: np.ndarray, nz: np.ndarray) -> np.ndarray:
        if name == "Earth":
            lat = np.arcsin(np.clip(ny, -1.0, 1.0))
            lon = np.arctan2(nz, nx)
            continents = np.sin(lon * 3.0) + np.cos(lat * 5.0)
            v = np.where(continents > 0.9, 0.28, 0.0)
            polar = np.clip((np.abs(ny) - 0.82) * 6.0, 0.0, 1.0) * 0.25
            return v + polar
        if name in {"Jupiter", "Saturn"}:
            lat = np.arcsin(np.clip(ny, -1.0, 1.0))
            return 0.12 * np.sin(lat * 26.0)
        if name == "Mars":
            lat = np.arcsin(np.clip(ny, -1.0, 1.0))
            lon = np.arctan2(nz, nx)
            return 0.08 * np.sin(lon * 7.0 + lat * 3.0)
        return np.zeros_like(nx)

    def _make_sprite(self, name: str, size: int) -> ImageTk.PhotoImage:
        size = max(4, size)
        y_idx, x_idx = np.ogrid[:size, :size]
        radius = size / 2.0
        x = (x_idx - radius + 0.5) / radius
        y = (y_idx - radius + 0.5) / radius
        rr = x * x + y * y
        inside = rr <= 1.0

        z = np.sqrt(np.clip(1.0 - rr, 0.0, 1.0))
        nx = x
        ny = y
        nz = z

        light = np.array([-0.85, -0.35, 0.4], dtype=np.float64)
        light = light / np.linalg.norm(light)
        diffuse = np.clip(nx * light[0] + ny * light[1] + nz * light[2], 0.0, 1.0)

        base_rgb = np.array(_hex_to_rgb(BODY_COLORS[name]), dtype=np.float64) / 255.0
        ambient = 0.22 if name != "Sun" else 0.5
        intensity = ambient + 0.78 * diffuse
        intensity += self._body_variation(name, nx, ny, nz)
        intensity = np.clip(intensity, 0.0, 1.35 if name == "Sun" else 1.1)

        rgb = np.zeros((size, size, 3), dtype=np.float64)
        rgb[..., 0] = base_rgb[0] * intensity
        rgb[..., 1] = base_rgb[1] * intensity
        rgb[..., 2] = base_rgb[2] * intensity

        if name == "Earth":
            lat = np.arcsin(np.clip(ny, -1.0, 1.0))
            lon = np.arctan2(nz, nx)
            land_mask = (np.sin(lon * 3.0) + np.cos(lat * 5.0)) > 0.9
            rgb[land_mask] = np.clip(
                rgb[land_mask] * np.array([0.52, 1.1, 0.52], dtype=np.float64),
                0.0,
                1.0,
            )

        alpha = np.zeros((size, size), dtype=np.uint8)
        alpha[inside] = 255

        if name == "Sun":
            glow = np.clip(1.0 - np.sqrt(rr), 0.0, 1.0)
            rgb = np.clip(rgb + np.stack([glow * 0.35, glow * 0.25, glow * 0.05], axis=-1), 0.0, 1.0)

        rgba = np.zeros((size, size, 4), dtype=np.uint8)
        rgba[..., :3] = np.clip(rgb * 255.0, 0.0, 255.0).astype(np.uint8)
        rgba[..., 3] = alpha
        image = Image.fromarray(rgba, mode="RGBA")
        return ImageTk.PhotoImage(image)

    def _sprite_for(self, name: str, radius_px: float) -> ImageTk.PhotoImage:
        key_radius = max(4, int(round((radius_px * 2.0) / 4.0) * 4))
        key = (name, key_radius)
        sprite = self.sprite_cache.get(key)
        if sprite is None:
            sprite = self._make_sprite(name, key_radius)
            self.sprite_cache[key] = sprite
        return sprite

    def _draw_body(self, name: str, sx: float, sy: float, radius: float) -> None:
        if radius < 2.0:
            color = BODY_COLORS[name]
            self.canvas.create_oval(sx - 1, sy - 1, sx + 1, sy + 1, fill=color, outline=color)
            return
        if radius > 350:
            # Avoid huge per-frame textures at extreme close zoom.
            color = BODY_COLORS[name]
            self.canvas.create_oval(
                sx - radius, sy - radius, sx + radius, sy + radius, fill=color, outline=""
            )
            return

        sprite = self._sprite_for(name, radius)
        self.tk_images.append(sprite)
        self.canvas.create_image(sx, sy, image=sprite)

    def _body_axis_vector(self, name: str) -> np.ndarray:
        tilt = math.radians(BODY_AXIS_TILT_DEG.get(name, 0.0))
        # Axis in ecliptic frame: tilt away from +Z in the Y-Z plane.
        axis = np.array([0.0, math.sin(tilt), math.cos(tilt)], dtype=np.float64)
        norm = float(np.linalg.norm(axis))
        if norm <= 1e-12:
            return np.array([0.0, 0.0, 1.0], dtype=np.float64)
        return axis / norm

    def _draw_selected_axis_and_equator(self, width: int, height: int) -> None:
        name = self.selected_body
        center = self.relative_positions.get(name)
        if center is None:
            return
        if self._body_draw_radius(name) < 18.0:
            return

        body_radius_au = BODY_RADIUS_KM.get(name, 1000.0) / AU_KM
        axis = self._body_axis_vector(name)

        # Axis line (through body center).
        p1 = center - axis * body_radius_au * 1.4
        p2 = center + axis * body_radius_au * 1.4
        sp1 = self._project_point(p1, width, height)
        sp2 = self._project_point(p2, width, height)
        if sp1 is not None and sp2 is not None:
            self.canvas.create_line(
                sp1[0], sp1[1], sp2[0], sp2[1], fill="#6fd3ff", width=2
            )

        # Equator ring (circle in plane perpendicular to axis), projected to screen.
        ref = np.array([1.0, 0.0, 0.0], dtype=np.float64)
        if abs(float(np.dot(ref, axis))) > 0.95:
            ref = np.array([0.0, 1.0, 0.0], dtype=np.float64)
        e1 = np.cross(axis, ref)
        e1_norm = float(np.linalg.norm(e1))
        if e1_norm <= 1e-12:
            return
        e1 = e1 / e1_norm
        e2 = np.cross(axis, e1)
        e2 = e2 / max(float(np.linalg.norm(e2)), 1e-12)

        points: list[float] = []
        samples = 64
        for i in range(samples + 1):
            t = (2.0 * math.pi * i) / samples
            w = center + body_radius_au * (math.cos(t) * e1 + math.sin(t) * e2)
            sp = self._project_point(w, width, height)
            if sp is None:
                continue
            points.extend([sp[0], sp[1]])
        if len(points) >= 6:
            self.canvas.create_line(*points, fill="#8ce99a", width=2, smooth=True)

    def _pick_body_at(self, x: int, y: int) -> str | None:
        hit_name = None
        hit_dist2 = float("inf")
        for name, (sx, sy, _depth) in self.last_screen_positions.items():
            radius = max(self._body_draw_radius(name), 6.0)
            dx = x - sx
            dy = y - sy
            d2 = (dx * dx) + (dy * dy)
            if d2 <= radius * radius and d2 < hit_dist2:
                hit_name = name
                hit_dist2 = d2
        return hit_name

    def _pick_moon_at(self, x: int, y: int) -> str | None:
        hit_name = None
        hit_dist2 = float("inf")
        for moon_name, (sx, sy, _depth) in self.last_moon_screen_positions.items():
            dx = x - sx
            dy = y - sy
            d2 = (dx * dx) + (dy * dy)
            if d2 <= 36.0 and d2 < hit_dist2:
                hit_name = moon_name
                hit_dist2 = d2
        return hit_name

    def _pick_lagrange_at(self, x: int, y: int) -> str | None:
        hit_label = None
        hit_dist2 = float("inf")
        for label, (sx, sy, _depth) in self.last_lagrange_screen_positions.items():
            dx = x - sx
            dy = y - sy
            d2 = (dx * dx) + (dy * dy)
            if d2 <= 64.0 and d2 < hit_dist2:
                hit_label = label
                hit_dist2 = d2
        return hit_label

    def _on_right_press(self, event: tk.Event) -> None:
        self.drag_last = (event.x, event.y)

    def _on_right_release(self, _event: tk.Event) -> None:
        self.drag_last = None

    def _on_right_drag(self, event: tk.Event) -> None:
        if self.drag_last is None:
            self.drag_last = (event.x, event.y)
            return
        dx = event.x - self.drag_last[0]
        dy = event.y - self.drag_last[1]
        self.drag_last = (event.x, event.y)

        self.yaw += dx * 0.005
        self.pitch -= dy * 0.005
        self.pitch = max(math.radians(-85), min(math.radians(85), self.pitch))
        self._render()

    def _on_middle_press(self, event: tk.Event) -> None:
        self.pan_last = (event.x, event.y)

    def _on_middle_release(self, _event: tk.Event) -> None:
        self.pan_last = None

    def _on_middle_drag(self, event: tk.Event) -> None:
        if self.locked_body is not None:
            self.pan_last = (event.x, event.y)
            return
        if self.pan_last is None:
            self.pan_last = (event.x, event.y)
            return

        dx = event.x - self.pan_last[0]
        dy = event.y - self.pan_last[1]
        self.pan_last = (event.x, event.y)

        width = max(self.canvas.winfo_width(), 1)
        height = max(self.canvas.winfo_height(), 1)
        right, up, _forward = self._camera_basis()
        world_per_px = self.camera_distance / (min(width, height) * self.focal_factor)
        scale = world_per_px * 2.0
        self.camera_focus -= (right * dx - up * dy) * scale
        self._render()

    def _on_mouse_wheel(self, event: tk.Event) -> None:
        if event.delta > 0:
            self.camera_distance *= 0.92
        else:
            self.camera_distance *= 1.08

        min_distance = self.scene_radius * 0.02
        if self.locked_body is not None:
            body_radius_au = BODY_RADIUS_KM[self.locked_body] / AU_KM
            min_distance = max(body_radius_au * 1.01, self.scene_radius * 1e-7)
        self.camera_distance = max(min_distance, min(self.scene_radius * 10.0, self.camera_distance))
        self._render()

    def _on_left_press(self, event: tk.Event) -> None:
        self.left_press_pos = (event.x, event.y)
        if self.resize_handle_center is None:
            return
        hx, hy = self.resize_handle_center
        dx = event.x - hx
        dy = event.y - hy
        if (dx * dx) + (dy * dy) <= (self.resize_handle_radius + 3.0) ** 2:
            self.resizing_info_panel = True
            self.resize_drag_start_canvas = (event.x, event.y)
            self.info_panel_start_size = (self.info_panel_width, self.info_panel_height)

    def _on_left_drag(self, event: tk.Event) -> None:
        if not self.resizing_info_panel:
            return
        if self.resize_drag_start_canvas is None or self.info_panel_start_size is None:
            return
        dx = self.resize_drag_start_canvas[0] - event.x
        dy = self.resize_drag_start_canvas[1] - event.y
        canvas_w = max(self.canvas.winfo_width(), 1)
        canvas_h = max(self.canvas.winfo_height(), 1)
        new_width = self.info_panel_start_size[0] + dx
        new_height = self.info_panel_start_size[1] + dy
        self.info_panel_width = int(max(360, min(canvas_w - 40, new_width)))
        self.info_panel_height = int(max(220, min(canvas_h - 40, new_height)))
        self._render()

    def _on_left_release(self, event: tk.Event) -> None:
        if self.resizing_info_panel:
            self.resizing_info_panel = False
            self.resize_drag_start_canvas = None
            self.info_panel_start_size = None
            self.left_press_pos = None
            return
        if self.skip_next_left_release_click:
            self.skip_next_left_release_click = False
            self.left_press_pos = None
            return
        self._on_left_click(event)
        self.left_press_pos = None

    def _on_left_click(self, event: tk.Event) -> None:
        hit_moon = self._pick_moon_at(event.x, event.y) if self.show_moons else None
        if hit_moon is not None:
            self.selected_moon_name = hit_moon
            self.selected_lagrange_label = None
            if self.show_lagrange:
                parent = self.selected_body
                if parent in MOON_IDS_BY_PLANET:
                    self.lagrange_primary = parent
                    self.lagrange_secondary = self._moon_token(parent, hit_moon)
            self._render()
            return

        hit_lagrange = self._pick_lagrange_at(event.x, event.y) if self.show_lagrange else None
        if hit_lagrange is not None:
            self.selected_lagrange_label = hit_lagrange
            self.selected_moon_name = None
            self._render()
            return

        hit_name = self._pick_body_at(event.x, event.y)
        if hit_name is not None:
            self.selected_body = hit_name
            self.selected_moon_name = None
            self.selected_lagrange_label = None
            if self.show_lagrange and hit_name != self.lagrange_primary:
                self.lagrange_secondary = hit_name
        else:
            self.selected_moon_name = None
            self.selected_lagrange_label = None
        self._render()

    def _on_left_double_click(self, event: tk.Event) -> None:
        self.skip_next_left_release_click = True
        hit_name = self._pick_body_at(event.x, event.y)
        if hit_name is None:
            # Double-click empty space to unlock.
            if self.locked_body is not None:
                self.locked_body = None
            self.selected_moon_name = None
            self._render()
            return

        if self.locked_body == hit_name:
            # Double-clicking the locked body toggles unlock.
            self.locked_body = None
        else:
            self.selected_body = hit_name
            self.selected_moon_name = None
            self.selected_lagrange_label = None
            self.locked_body = hit_name
            if hit_name != self.lagrange_primary:
                self.lagrange_secondary = hit_name
        self._render()

    def _on_lock_earth(self, _event: tk.Event) -> None:
        self.selected_body = "Earth"
        self.selected_moon_name = None
        self.selected_lagrange_label = None
        self.locked_body = "Earth"
        if self.lagrange_primary != "Earth":
            self.lagrange_secondary = "Earth"
        self._render()

    def _on_lock_sun(self, _event: tk.Event) -> None:
        self.selected_body = "Sun"
        self.selected_moon_name = None
        self.selected_lagrange_label = None
        self.locked_body = "Sun"
        if self.lagrange_primary != "Sun":
            self.lagrange_secondary = "Sun"
        self._render()

    def _on_unlock(self, _event: tk.Event) -> None:
        self.locked_body = None
        self.selected_moon_name = None
        self.selected_lagrange_label = None
        self._render()

    def _on_toggle_lagrange(self, _event: tk.Event) -> None:
        self.show_lagrange = not self.show_lagrange
        if not self.show_lagrange:
            self.selected_lagrange_label = None
        self._render()

    def _on_toggle_belts(self, _event: tk.Event) -> None:
        self.show_belts = not self.show_belts
        self._render()

    def _on_toggle_orbits(self, _event: tk.Event) -> None:
        self.show_orbits = not self.show_orbits
        self._render()

    def _on_toggle_moons(self, _event: tk.Event) -> None:
        self.show_moons = not self.show_moons
        self._render()

    def _draw_orbits(self, width: int, height: int) -> None:
        sun = self.relative_positions["Sun"]
        name = self.selected_body
        if name == "Sun":
            return
        r_vec = self.relative_positions.get(name)
        v_vec = self.relative_velocities.get(name)
        if r_vec is None or v_vec is None:
            return
        r_norm = float(np.linalg.norm(r_vec))
        if r_norm <= 1e-12:
            return
        u = r_vec / r_norm
        h = np.cross(r_vec, v_vec)
        h_norm = float(np.linalg.norm(h))
        if h_norm <= 1e-12:
            return
        h_hat = h / h_norm
        w = np.cross(h_hat, u)
        w_norm = float(np.linalg.norm(w))
        if w_norm <= 1e-12:
            return
        w = w / w_norm

        points: list[float] = []
        steps = 180
        for i in range(steps + 1):
            t = (2.0 * math.pi * i) / steps
            world = sun + r_norm * (math.cos(t) * u + math.sin(t) * w)
            projected = self._project_point(world, width, height)
            if projected is None:
                continue
            points.extend([projected[0], projected[1]])

        if len(points) >= 6:
            self.canvas.create_line(
                *points,
                fill=BODY_COLORS.get(name, "#888888"),
                width=1,
                smooth=True,
            )

    def _draw_selected_moons(self, width: int, height: int) -> None:
        self.last_moon_screen_positions = {}
        if not self.show_moons:
            return
        parent = self.selected_body
        if parent not in MOON_IDS_BY_PLANET:
            return
        moons = self.moon_positions_by_parent.get(parent, {})
        if not moons:
            return

        parent_radius_px = self._body_draw_radius(parent)
        show_labels = parent_radius_px >= 14.0

        for moon_name, moon_pos in moons.items():
            projected = self._project_point(moon_pos, width, height)
            if projected is None:
                continue
            mx, my, md = projected
            self.last_moon_screen_positions[moon_name] = (mx, my, md)
            focal_px = min(width, height) * self.focal_factor
            moon_radius_au = MOON_RADIUS_KM.get(moon_name, 100.0) / AU_KM
            moon_radius_px = max((moon_radius_au / md) * focal_px, 1.0)
            moon_color = MOON_COLORS.get(moon_name, "#d9d9d9")
            self.canvas.create_oval(
                mx - moon_radius_px,
                my - moon_radius_px,
                mx + moon_radius_px,
                my + moon_radius_px,
                fill=moon_color,
                outline=moon_color,
            )
            if show_labels:
                self.canvas.create_text(
                    mx + 6,
                    my - 6,
                    text=moon_name,
                    fill="#cfd3da",
                    anchor="sw",
                    font=("Consolas", 9),
                )
        if self.selected_moon_name is not None:
            sel = self.last_moon_screen_positions.get(self.selected_moon_name)
            if sel is not None:
                sx, sy, _sd = sel
                moon_radius_au = MOON_RADIUS_KM.get(self.selected_moon_name, 100.0) / AU_KM
                focal_px = min(width, height) * self.focal_factor
                moon_radius_px = max((moon_radius_au / _sd) * focal_px, 1.0)
                ring = max(moon_radius_px + 4.0, 7.0)
                self.canvas.create_oval(
                    sx - ring,
                    sy - ring,
                    sx + ring,
                    sy + ring,
                    outline="#00ffff",
                    width=2,
                )

    def _draw_selected_moon_orbit(self, width: int, height: int) -> None:
        moon_name = self.selected_moon_name
        parent = self.selected_body
        if moon_name is None:
            return
        moon_pos = self.moon_positions_by_parent.get(parent, {}).get(moon_name)
        moon_vel = self.moon_velocities_by_parent.get(parent, {}).get(moon_name)
        parent_pos = self.relative_positions.get(parent)
        parent_vel = self.relative_velocities.get(parent)
        if moon_pos is None or moon_vel is None or parent_pos is None or parent_vel is None:
            return

        r_vec = moon_pos - parent_pos
        v_vec = moon_vel - parent_vel
        r_norm = float(np.linalg.norm(r_vec))
        if r_norm <= 1e-12:
            return
        u = r_vec / r_norm
        h = np.cross(r_vec, v_vec)
        h_norm = float(np.linalg.norm(h))
        if h_norm <= 1e-12:
            return
        h_hat = h / h_norm
        w = np.cross(h_hat, u)
        w_norm = float(np.linalg.norm(w))
        if w_norm <= 1e-12:
            return
        w = w / w_norm

        points: list[float] = []
        steps = 180
        for i in range(steps + 1):
            t = (2.0 * math.pi * i) / steps
            world = parent_pos + r_norm * (math.cos(t) * u + math.sin(t) * w)
            projected = self._project_point(world, width, height)
            if projected is None:
                continue
            points.extend([projected[0], projected[1]])
        if len(points) >= 6:
            self.canvas.create_line(
                *points,
                fill="#cfd3da",
                width=1,
                smooth=True,
            )

    def _next_body(self, current: str, exclude: str) -> str:
        if current not in self.body_order:
            return self.body_order[0]
        idx = self.body_order.index(current)
        for i in range(1, len(self.body_order) + 1):
            candidate = self.body_order[(idx + i) % len(self.body_order)]
            if candidate != exclude:
                return candidate
        return current

    def _on_cycle_lagrange_secondary(self, _event: tk.Event) -> None:
        candidates = self._secondary_candidates()
        if not candidates:
            return
        if self.lagrange_secondary not in candidates:
            self.lagrange_secondary = candidates[0]
        else:
            idx = candidates.index(self.lagrange_secondary)
            self.lagrange_secondary = candidates[(idx + 1) % len(candidates)]
        self.selected_lagrange_label = None
        self._render()

    def _on_cycle_lagrange_primary(self, _event: tk.Event) -> None:
        self.lagrange_primary = self._next_body(self.lagrange_primary, self.lagrange_secondary)
        self.selected_lagrange_label = None
        self._render()

    def _on_resize(self, _event: tk.Event) -> None:
        self._render()

    def _compute_lagrange_points(self, primary_name: str, secondary_name: str) -> dict[str, np.ndarray]:
        if primary_name == secondary_name:
            return {}

        primary_state = self._resolve_target_state(primary_name)
        secondary_state = self._resolve_target_state(secondary_name)
        if primary_state is None or secondary_state is None:
            return {}
        p1, v1, m1 = primary_state
        p2, v2, m2 = secondary_state

        r_vec = p2 - p1
        r = float(np.linalg.norm(r_vec))
        if r <= 1e-12:
            return {}

        u = r_vec / r
        mu = m2 / (m1 + m2)
        h = np.cross(r_vec, v2 - v1)
        h_norm = float(np.linalg.norm(h))
        if h_norm <= 1e-12:
            h_hat = np.array([0.0, 0.0, 1.0], dtype=np.float64)
        else:
            h_hat = h / h_norm
        v_dir = np.cross(h_hat, u)
        v_norm = float(np.linalg.norm(v_dir))
        if v_norm <= 1e-12:
            v_dir = np.array([0.0, 1.0, 0.0], dtype=np.float64)
        else:
            v_dir = v_dir / v_norm

        d = r * (mu / 3.0) ** (1.0 / 3.0)
        l1 = p1 + (r_vec - u * d)
        l2 = p1 + (r_vec + u * d)
        l3 = p1 + (-u * (r * (1.0 + (5.0 * mu / 12.0))))
        l4 = p1 + ((0.5 * r * u) + (math.sqrt(3.0) * 0.5 * r * v_dir))
        l5 = p1 + ((0.5 * r * u) - (math.sqrt(3.0) * 0.5 * r * v_dir))
        return {"L1": l1, "L2": l2, "L3": l3, "L4": l4, "L5": l5}

    def _lagrange_stability(
        self, label: str, primary_name: str, secondary_name: str
    ) -> tuple[str, float, float]:
        primary_state = self._resolve_target_state(primary_name)
        secondary_state = self._resolve_target_state(secondary_name)
        if primary_state is None or secondary_state is None:
            return "Unknown", 0.0, 0.0
        _p1, _v1, m1 = primary_state
        _p2, _v2, m2 = secondary_state
        mu = m2 / (m1 + m2)

        if label in {"L1", "L2", "L3"}:
            return "Unstable (saddle equilibrium)", 0.0, mu

        if label in {"L4", "L5"}:
            if mu < MU_ROUTH:
                margin = 1.0 - (mu / MU_ROUTH)
                return "Conditionally stable (small perturbations)", max(0.0, min(1.0, margin)), mu
            exceed = (mu / MU_ROUTH) - 1.0
            return "Unstable (mass ratio above Routh limit)", max(0.0, 1.0 - min(exceed, 1.0)), mu

        return "Unknown", 0.0, mu

    def _velocity_info(self, name: str) -> tuple[float, np.ndarray, float, float]:
        v = self.relative_velocities[name]
        speed_au_day = float(np.linalg.norm(v))
        speed_km_s = speed_au_day * AU_KM / SECONDS_PER_DAY
        if speed_au_day > 0:
            unit = v / speed_au_day
        else:
            unit = np.array([0.0, 0.0, 0.0], dtype=np.float64)
        lon_deg = math.degrees(math.atan2(unit[1], unit[0]))
        lat_deg = math.degrees(math.atan2(unit[2], math.sqrt(unit[0] * unit[0] + unit[1] * unit[1])))
        return speed_km_s, unit, lon_deg, lat_deg

    def _draw_info_panel(self, width: int, height: int) -> None:
        name = self.selected_body
        p = self.relative_positions[name]
        v = self.relative_velocities[name]
        speed_km_s, unit_dir, lon_deg, lat_deg = self._velocity_info(name)
        mass = BODY_MASS_KG.get(name)
        lag_label = self.selected_lagrange_label
        moon_name = self.selected_moon_name

        min_height_for_content = 220 if lag_label is not None else 180
        panel_width = int(min(width - 20, max(360, self.info_panel_width)))
        panel_height = int(min(height - 20, max(min_height_for_content, self.info_panel_height)))
        x1 = width - panel_width - 20
        y1 = height - panel_height - 4
        x2 = width - 20
        y2 = height - 4
        self.info_panel_rect = (x1, y1, x2, y2)
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#101010", outline="#404040")
        hx = x1
        hy = y1
        self.resize_handle_center = (hx, hy)
        hr = self.resize_handle_radius
        self.canvas.create_oval(
            hx - hr,
            hy - hr,
            hx + hr,
            hy + hr,
            fill="#ffffff",
            outline="#ffffff",
            width=1,
        )

        lines = [
            f"Selected: {name}",
            f"Lock: {self.locked_body if self.locked_body is not None else 'None'}",
            (
                f"Lagrange Pair: {self._target_label(self.lagrange_primary)} -> "
                f"{self._target_label(self.lagrange_secondary)} "
                f"({'ON' if self.show_lagrange else 'OFF'})"
            ),
            f"Belts: {'ON' if self.show_belts else 'OFF'}",
            f"Orbits: {'ON' if self.show_orbits else 'OFF'} (R)",
            f"Moons: {'ON' if self.show_moons else 'OFF'} (M)",
        ]

        if moon_name is not None and self.selected_body in self.moon_positions_by_parent:
            moon_pos = self.moon_positions_by_parent[self.selected_body].get(moon_name)
            moon_vel = self.moon_velocities_by_parent.get(self.selected_body, {}).get(moon_name)
            if moon_pos is not None and moon_vel is not None:
                parent_pos = self.relative_positions[self.selected_body]
                parent_vel = self.relative_velocities[self.selected_body]
                moon_speed_au_day = float(np.linalg.norm(moon_vel))
                moon_speed_km_s = moon_speed_au_day * AU_KM / SECONDS_PER_DAY
                if moon_speed_au_day > 0:
                    moon_unit = moon_vel / moon_speed_au_day
                else:
                    moon_unit = np.array([0.0, 0.0, 0.0], dtype=np.float64)
                moon_lon = math.degrees(math.atan2(moon_unit[1], moon_unit[0]))
                moon_lat = math.degrees(
                    math.atan2(moon_unit[2], math.sqrt(moon_unit[0] * moon_unit[0] + moon_unit[1] * moon_unit[1]))
                )
                rel_parent_pos = moon_pos - parent_pos
                rel_parent_vel = moon_vel - parent_vel
                moon_mass = MOON_MASS_KG.get(moon_name)
                lines.extend(
                    [
                        f"Moon Selected: {moon_name} (parent: {self.selected_body})",
                        f"Mass: {moon_mass:.6e} kg" if moon_mass is not None else "Mass: N/A",
                        f"Position rel {self.selected_body} (AU): x={rel_parent_pos[0]:+.9f} y={rel_parent_pos[1]:+.9f} z={rel_parent_pos[2]:+.9f}",
                        f"Velocity rel {self.selected_body} (AU/day): vx={rel_parent_vel[0]:+.9f} vy={rel_parent_vel[1]:+.9f} vz={rel_parent_vel[2]:+.9f}",
                        f"Speed rel Sun: {moon_speed_km_s:.4f} km/s",
                        f"Direction unit vector: x={moon_unit[0]:+.5f} y={moon_unit[1]:+.5f} z={moon_unit[2]:+.5f}",
                        f"Direction angles (ecliptic): lon={moon_lon:+.2f} deg lat={moon_lat:+.2f} deg",
                    ]
                )
        else:
            lines.extend(
                [
                    f"Mass: {mass:.6e} kg" if mass is not None else "Mass: N/A",
                    f"Position rel Sun (AU): x={p[0]:+.9f} y={p[1]:+.9f} z={p[2]:+.9f}",
                    f"Velocity rel Sun (AU/day): vx={v[0]:+.9f} vy={v[1]:+.9f} vz={v[2]:+.9f}",
                    f"Speed: {speed_km_s:.4f} km/s",
                    f"Direction unit vector: x={unit_dir[0]:+.5f} y={unit_dir[1]:+.5f} z={unit_dir[2]:+.5f}",
                    f"Direction angles (ecliptic): lon={lon_deg:+.2f} deg lat={lat_deg:+.2f} deg",
                ]
            )
        if lag_label is not None:
            stability_text, score, mu = self._lagrange_stability(
                lag_label, self.lagrange_primary, self.lagrange_secondary
            )
            lines.append(f"Lagrange Selected: {lag_label} ({self.lagrange_primary}-{self.lagrange_secondary})")
            lines.append(
                f"Stability: {stability_text} | Score={score*100:.1f}/100 | mu={mu:.6f} (mu_crit={MU_ROUTH:.6f})"
            )
        self.canvas.create_text(
            x1 + 26,
            y1 + 12,
            text="\n".join(lines),
            fill="white",
            anchor="nw",
            justify="left",
            width=panel_width - 24,
            font=("Consolas", 10),
        )

    def _draw_controls_panel(self) -> None:
        x1, y1 = 14, 12
        panel_width = 720
        panel_height = 116
        x2, y2 = x1 + panel_width, y1 + panel_height
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="#101010", outline="#404040")
        controls = [
            "Controls",
            "RMB drag: Orbit | MMB drag: Pan | Wheel: Zoom",
            "LMB: Select/Unlock | Double LMB: Lock target",
            "E: Earth lock | S: Sun lock | L: Toggle Lagrange points | B: Toggle belts | R: Toggle orbits | M: Toggle moons",
            "O: Next primary | P: Next secondary (includes moons of locked planet) | Click L-point: Stability | Esc: Unlock",
        ]
        self.canvas.create_text(
            x1 + 10,
            y1 + 10,
            text="\n".join(controls),
            fill="white",
            anchor="nw",
            justify="left",
            width=panel_width - 20,
            font=("Consolas", 10),
        )

    def _render(self) -> None:
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width < 10 or height < 10:
            return

        self.canvas.delete("all")
        self.tk_images = []
        self.last_screen_positions = {}
        self.last_lagrange_screen_positions = {}

        draw_items: list[tuple[float, str, float, float]] = []
        for name, point in self.relative_positions.items():
            projected = self._project_point(point, width, height)
            if projected is None:
                continue
            sx, sy, depth = projected
            draw_items.append((depth, name, sx, sy))
            self.last_screen_positions[name] = (sx, sy, depth)

        if self.show_orbits:
            self._draw_orbits(width, height)
        self._draw_selected_moon_orbit(width, height)

        if self.show_belts:
            for pt in self.main_belt_points:
                projected = self._project_point(pt, width, height)
                if projected is None:
                    continue
                bx, by, _bz = projected
                self.canvas.create_rectangle(
                    bx, by, bx + 1, by + 1, outline="#8f8f8f", fill="#8f8f8f"
                )
            for pt in self.kuiper_belt_points:
                projected = self._project_point(pt, width, height)
                if projected is None:
                    continue
                bx, by, _bz = projected
                self.canvas.create_rectangle(
                    bx, by, bx + 1, by + 1, outline="#5f7aa6", fill="#5f7aa6"
                )

        draw_items.sort(reverse=True)
        for _depth, name, sx, sy in draw_items:
            radius = self._body_draw_radius(name)
            if radius <= 0:
                continue
            self._draw_body(name, sx, sy, radius)
            if name == "Sun":
                # Distinct Sun label for readability against dense scenes.
                self.canvas.create_text(
                    sx + 15,
                    sy - 13,
                    text="SUN",
                    fill="#000000",
                    anchor="sw",
                    font=("Consolas", 12, "bold"),
                )
                self.canvas.create_text(
                    sx + 14,
                    sy - 14,
                    text="SUN",
                    fill="#ffe88a",
                    anchor="sw",
                    font=("Consolas", 12, "bold"),
                )
            else:
                self.canvas.create_text(
                    sx + 8,
                    sy - 8,
                    text=name,
                    fill="white",
                    anchor="sw",
                    font=("Consolas", 10),
                )

        self._draw_selected_moons(width, height)

        if self.show_lagrange:
            points = self._compute_lagrange_points(self.lagrange_primary, self.lagrange_secondary)
            for label, point in points.items():
                projected = self._project_point(point, width, height)
                if projected is None:
                    continue
                lx, ly, _lz = projected
                self.last_lagrange_screen_positions[label] = (lx, ly, _lz)
                r = 4
                self.canvas.create_oval(
                    lx - r,
                    ly - r,
                    lx + r,
                    ly + r,
                    fill="#ff66ff",
                    outline="#ff66ff",
                )
                self.canvas.create_text(
                    lx + 8,
                    ly - 8,
                    text=label,
                    fill="#ff99ff",
                    anchor="sw",
                    font=("Consolas", 10),
                )
            if self.selected_lagrange_label is not None:
                picked = self.last_lagrange_screen_positions.get(self.selected_lagrange_label)
                if picked is not None:
                    px, py, _pd = picked
                    self.canvas.create_oval(
                        px - 8,
                        py - 8,
                        px + 8,
                        py + 8,
                        outline="#ff3333",
                        width=2,
                    )

        selected_proj = self.last_screen_positions.get(self.selected_body)
        if selected_proj is not None:
            sx, sy, _depth = selected_proj
            ring = max(self._body_draw_radius(self.selected_body) + 4.0, 10.0)
            ring_color = "#ff4040" if self.locked_body == self.selected_body else "#00ffff"
            self.canvas.create_oval(
                sx - ring,
                sy - ring,
                sx + ring,
                sy + ring,
                outline=ring_color,
                width=2,
            )
        self._draw_selected_axis_and_equator(width, height)

        self._draw_controls_panel()
        self.canvas.create_text(
            18,
            136,
            text=f"Epoch (UTC): {self.epoch.isoformat()}",
            fill="white",
            anchor="nw",
            font=("Consolas", 11),
        )
        self._draw_info_panel(width, height)

    def run(self) -> None:
        self.root.mainloop()


def draw_positions_once() -> None:
    epoch, states, moon_states = fetch_all_body_states_au_once()
    sun = states["Sun"]
    sun_pos = np.array([sun.x, sun.y, sun.z], dtype=np.float64)
    sun_vel = np.array([sun.vx, sun.vy, sun.vz], dtype=np.float64)

    relative_positions = {}
    relative_velocities = {}
    for name, state in states.items():
        pos = np.array([state.x, state.y, state.z], dtype=np.float64)
        vel = np.array([state.vx, state.vy, state.vz], dtype=np.float64)
        relative_positions[name] = pos - sun_pos
        relative_velocities[name] = vel - sun_vel

    moon_positions_by_parent: dict[str, dict[str, np.ndarray]] = {}
    moon_velocities_by_parent: dict[str, dict[str, np.ndarray]] = {}
    for parent, moons in moon_states.items():
        moon_positions_by_parent[parent] = {}
        moon_velocities_by_parent[parent] = {}
        for moon_name, moon_state in moons.items():
            moon_pos = np.array([moon_state.x, moon_state.y, moon_state.z], dtype=np.float64)
            moon_vel = np.array([moon_state.vx, moon_state.vy, moon_state.vz], dtype=np.float64)
            moon_positions_by_parent[parent][moon_name] = moon_pos - sun_pos
            moon_velocities_by_parent[parent][moon_name] = moon_vel - sun_vel

    Solar3DViewer(
        epoch,
        relative_positions,
        relative_velocities,
        moon_positions_by_parent,
        moon_velocities_by_parent,
    ).run()


def main() -> None:
    draw_positions_once()


if __name__ == "__main__":
    main()
