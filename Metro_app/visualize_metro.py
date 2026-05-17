import json
import folium
import webbrowser
import tempfile
import sys
from pathlib import Path
from typing import Tuple, Optional


def get_available_cities():
    data_dir = Path(__file__).parent / "Data files"
    cities = []
    for json_file in data_dir.glob("*.json"):
        if json_file.stem == "mini_reseau":
            continue
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cities.append((json_file.stem, data.get('nom', json_file.stem)))
        except Exception:
            continue
    return sorted(cities)


class MetroMapVisualizer:
    def __init__(self, data_path: str, city_code: Optional[str] = None):
        # accept city_code for backward compatibility with the interface
        self.data_path = Path(data_path)
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.map = None

    def _get_coord(self, name: str) -> Optional[Tuple[float, float]]:
        coords = self.data.get('stations_coordonnees', {}).get(name)
        if coords and 'latitude' in coords and 'longitude' in coords:
            return coords['latitude'], coords['longitude']
        return None

    def _map_center(self) -> Tuple[float, float]:
        coords = [c for c in self.data.get('stations_coordonnees', {}).values() if c and 'latitude' in c and 'longitude' in c]
        if not coords:
            return 48.8566, 2.3522
        lats = [c['latitude'] for c in coords]
        lons = [c['longitude'] for c in coords]
        return sum(lats) / len(lats), sum(lons) / len(lons)

    def create_map(self, zoom_start: int = 12, save_path: Optional[str] = None) -> folium.Map:
        center = self._map_center()
        self.map = folium.Map(location=center, zoom_start=zoom_start, tiles='OpenStreetMap')

        colors_map = {
            "jaune": "gold", "bleu": "blue", "olive": "olive", "magenta": "purple",
            "orange": "darkorange", "vert clair": "lightgreen", "rose": "pink",
            "lilas": "darkviolet", "jaune-vert": "yellowgreen", "ocre": "goldenrod",
            "marron": "brown", "vert foncé": "darkgreen", "bleu clair": "cadetblue",
            "violet": "purple", "rouge": "red", "bleue": "blue", "green": "green",
            "black": "black", "gray": "gray"
        }

        # draw each line using its configured color when available
        for line_id, line in self.data.get('lignes', {}).items():
            stations = line.get('stations', [])
            raw_color = (line.get('couleur') or '').strip()
            if raw_color.startswith('#'):
                color = raw_color
            else:
                color = colors_map.get(raw_color.lower(), 'blue')

            for i in range(len(stations) - 1):
                a = stations[i]
                b = stations[i + 1]
                ca = self._get_coord(a)
                cb = self._get_coord(b)
                if ca and cb:
                    folium.PolyLine([ca, cb], color=color, weight=4, opacity=0.8).add_to(self.map)

        # add station markers in the order they appear on lines (preserve given ordering)
        stations_added = set()
        for line_id, line in self.data.get('lignes', {}).items():
            stations = line.get('stations', [])
            for entry in stations:
                # entry may be a string or an object with a 'nom' field
                if isinstance(entry, str):
                    name = entry
                elif isinstance(entry, dict):
                    name = entry.get('nom') or entry.get('name')
                else:
                    continue

                if not name or name in stations_added:
                    continue

                c = self.data.get('stations_coordonnees', {}).get(name)
                if c and 'latitude' in c and 'longitude' in c:
                    folium.CircleMarker(location=(c['latitude'], c['longitude']), radius=4, popup=name, color='darkblue', fill=True, fillColor='lightblue').add_to(self.map)
                    stations_added.add(name)

        if save_path:
            self.map.save(save_path)
        return self.map

    def show(self):
        if not self.map:
            self.create_map()
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp:
            self.map.save(tmp.name)
            webbrowser.open(f'file://{Path(tmp.name).absolute()}')

    def render_html(self) -> str:
        if not self.map:
            self.create_map()
        return self.map.get_root().render()


def visualize_metro(city_code: str) -> bool:
    data_file = Path(__file__).parent / 'Data files' / f'{city_code}.json'
    if not data_file.exists():
        print(f'File not found: {city_code}.json')
        return False
    vis = MetroMapVisualizer(str(data_file))
    out = Path(__file__).parent / f'{city_code}_map.html'
    vis.create_map(save_path=str(out))
    vis.show()
    print(f'Map created: {out}')
    return True


def main():
    available = get_available_cities()
    if len(sys.argv) > 1:
        code = sys.argv[1].lower()
        codes = [c for c, _ in available]
        if code in codes:
            visualize_metro(code)
            return
        else:
            print('City not found')

    print('Available cities:')
    for i, (c, name) in enumerate(available, 1):
        print(f'  {i}. {name} ({c})')
    choice = input('Select city (number or code): ').strip().lower()
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(available):
            visualize_metro(available[idx][0])
            return
    else:
        visualize_metro(choice)


if __name__ == '__main__':
    main()
