# NYC Restaurant Week 2026 Map built with React

An interactive map showing participating restaurants for NYC Restaurant Week 2026 (Jan 20 - Feb 12)

My pipeline **nyc_restaurant_pipeline.py**:
1) uses Selenium to scrape the restaurant name, cuisine type, and neighborhood from https://www.nyctourism.com/restaurant-week/.
   It scrapes the data from the 12 cards on each of the main 54 pages and 5 cards on the 55th (last) page, and compiles everything
   into a csv file
2) The pipeline pauses at this point so that you can manually review the csv file. (This is because I noticed that 3 restaurants
   had neighborhood info for Cuisine because on the website, that’s what data had been inserted into that html section. So I did
   have to manually enter the info for those 3 restaurants)
3) After updating anything you need to, when you're ready to continue, you hit Enter
4) Then, it appends each entry in the “Neighborhood” column with “, New York, NY”, so that it’d say “Brooklyn Heights, New York, NY”,
   “Soho, New York, NY”, etc
5) Then, it makes a Google Places API call to add the actual addresses of the restaurants
6) Then, it makes a Google Geocoding API call to convert the addresses into latitude and longitude and add those new columns
7) Then, it converts the csv file to json
8) Then, it creates the interactive map with React and Leaflet

## Process
Run the file **nyc_restaurant_pipeline.py**, but make sure to add your Google API key online 29. It'll stop after step 1 so you can manually
review the produced csv file. Once you're ready to continue, hit Enter, and by the end, it'll produce your **restaurant_map.html**
file.

## Technologies Used
- **React 18** (loaded via CDN)
- **Leaflet.js** for interactive mapping
- **Babel Standalone** for JSX transformation
- **Google Places, Geocoding APIs**
- No build tools or npm required!

## Features
- Interactive map of all participating restaurants
- Filter by cuisine type
- Search by restaurant name
- Hover over markers for restaurant details
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
