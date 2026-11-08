# StreetWise

**A turn-by-turn GPS navigator for Madrid, built on OpenStreetMap data and graph algorithms implemented from scratch.**

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![NetworkX](https://img.shields.io/badge/NetworkX-graphs-orange)
![OSMnx](https://img.shields.io/badge/OSMnx-OpenStreetMap-7EBC6F?logo=openstreetmap&logoColor=white)

StreetWise turns two Madrid street addresses into a route: it geocodes the addresses, finds the nearest intersections in the city's road network, computes the optimal path with a hand-written **Dijkstra**, prints spoken-style driving directions, and draws the route over an OpenStreetMap base map.

> Project for the *Discrete Mathematics* course, Universidad Pontificia Comillas (ICAI).

---

## How it works

1. **Address geocoding** (`callejero.py`): loads Madrid's official street directory (~214k addresses), converts DMS coordinates (degrees/minutes/seconds) to decimal degrees with regular expressions, and normalises names (upper case, no accents). Addresses are parsed as `street type + particle + name, number`. If there is no exact match, the closest street name is chosen with **fuzzy matching** (`difflib`, similarity ≥ 0.7).
2. **Road graph** (`callejero.py`): downloads Madrid's drivable network with OSMnx (cached as GraphML), collapses the multigraph into a simple directed graph, removes self-loops, cleans the OSM attributes (road type, street name, speed limits, with defaults per road type), and adds a **travel time** to every edge.
3. **Routing** (`grafo_pesado.py`, `gps.py`): Dijkstra with a binary heap and pluggable weight functions. Three modes:
   - **Shortest**: edge length in metres.
   - **Fastest**: travel time at the speed limit.
   - **Fastest with traffic lights**: travel time plus an expected 30 s stop with 80 % probability at each intersection.
4. **Turn-by-turn directions** (`gps.py`): consecutive edges on the same street are merged, and turns are classified as left / right / straight using the sign of the **2D cross product** of the edge geometries at each intersection.
5. **Map display**: the route is drawn over an OpenStreetMap basemap with `contextily`.

The graph library also includes **Prim** and **Kruskal** minimum spanning tree algorithms; `test_grafo.py` exercises all of them on a random weighted graph.

## Example session

```
____NEW ROUTE____

Location of the origin: Calle de Alberto Aguilera, 23
Location of the destination: <street>, <number>
 Route calculation mode (1,2,3):
        1: Shortest route between the addresses: uses the total length.
        2. Fastest route between the addresses: uses the travel time.
        3. Fastest route accounting for traffic lights: uses the travel time.
2
Continue straight for <metres> metres on <street>
Turn <left|right> onto <street>
...
You have arrived at your destination!
```

## Getting started

```bash
git clone https://github.com/javmartineez/StreetWise.git
cd StreetWise
pip install -r requirements_gps.txt
```

1. Download Madrid's street directory with coordinates (*Callejero: direcciones vigentes con coordenadas*) from the [Madrid open data portal](https://datos.madrid.es) and save it as `direcciones.csv` in the project folder.
2. Run the navigator. The first run downloads the Madrid road network from OpenStreetMap and caches it as `madrid.graphml`:

```bash
python gps.py
```

Press ENTER on an empty prompt to quit. To check the graph algorithms on their own:

```bash
python test_grafo.py
```

## Project structure

```
StreetWise/
├── gps.py              # Navigator: route modes, turn-by-turn directions, map display
├── callejero.py        # Address directory loading, geocoding and road-graph processing
├── grafo_pesado.py     # Dijkstra, shortest path, Prim and Kruskal (from scratch)
├── test_grafo.py       # Quick check of the graph algorithms
└── requirements_gps.txt
```

## Tech stack

Python · NetworkX · OSMnx · pandas · Matplotlib · contextily · heapq · regular expressions

## Authors

- **Javier Martínez Berenguer** · [GitHub](https://github.com/javmartineez)
- **Javier Mochales López** · [GitHub](https://github.com/jmochales06)
