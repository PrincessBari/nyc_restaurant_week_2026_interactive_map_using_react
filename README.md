# NYC Restaurant Week 2026 Map built with React

An interactive map showing participating restaurants for NYC Restaurant Week 2026 (Jan 20 - Feb 12), built with React and Leaflet.

## Project Structure

- `index.html` - Main HTML file with embedded React components
- `index.js` - React component logic (reference copy)
- `styles.css` - Styling (reference copy)
- `restaurants.json` - Restaurant data with 653 locations and cuisine types

## Technologies Used
- **React 18** (loaded via CDN)
- **Leaflet.js** for interactive mapping
- **Babel Standalone** for JSX transformation
- No build tools or npm required!

## Features
- Interactive map of all participating restaurants
- Filter by cuisine type
- Search by restaurant name
- Click markers for restaurant details
- Mobile-responsive design

## How to Run Locally

1. Clone this repository
```bash
   git clone https://github.com/PrincessBari/nyc_restaurant_week_2026_interactive_map_using_react.git
   cd nyc_restaurant_week_2026_interactive_map_using_react
```

2. Start a local server (Python method)
```bash
   python3 -m http.server 8000
```

3. Open your browser to `http://localhost:8000`

That's it! No npm install, no build step needed.

## Live Demo

View the live site at: `https://PrincessBari.github.io/nyc_restaurant_week_2026_interactive_map_using_react`

## Data Source

Restaurant data sourced from NYC Restaurant Week 2026 participating locations: https://www.nyctourism.com/restaurant-week/
