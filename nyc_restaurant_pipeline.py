"""
NYC Restaurant Week Pipeline
=============================
Complete pipeline that:
1. Scrapes restaurant data from NYC Tourism website
2. Appends ", New York, NY" to neighborhoods
3. Fetches addresses using Google Places API
4. Fetches coordinates using Google Geocoding API
5. Converts CSV to JSON for the interactive map
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import csv
import time
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

API_KEY = "YOUR_GOOGLE_API_KEY_HERE"  # Replace with your actual API key

# ============================================================================
# STEP 1: WEB SCRAPING
# ============================================================================

def scrape_restaurant_week():
    """Scrape restaurant data from NYC Tourism website."""
    
    base_url = "https://www.nyctourism.com/restaurant-week/"
    all_restaurants = []
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run without browser window
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    print("=" * 80)
    print("STEP 1: WEB SCRAPING")
    print("=" * 80)
    print("\nInitializing browser...")
    
    # Initialize the driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window()
    
    try:
        page_count = 0
        max_pages = 55
        
        # Start at the main page
        driver.get(base_url)
        time.sleep(3)
        
        while page_count < max_pages:
            page_count += 1
            print(f"\nPage {page_count}/{max_pages}")
            
            # Handle lazy loading by scrolling
            for scroll_step in range(5):
                driver.execute_script(f"window.scrollTo(0, {(scroll_step + 1) * 500});")
                time.sleep(0.3)
            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Wait for restaurant cards to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h3.CardHeading_headline__qu1q3"))
                )
            except:
                print("  ⚠ Timeout waiting for restaurant cards")
                break
            
            # Find all restaurant names and tags
            restaurant_names = driver.find_elements(By.CSS_SELECTOR, "h3.CardHeading_headline__qu1q3")
            tag_containers = driver.find_elements(By.CSS_SELECTOR, "div.PromotionCardGrid_taglines__qTyHJ")
            
            num_restaurants = len(restaurant_names)
            print(f"Found {num_restaurants} restaurants on this page")
            
            if num_restaurants == 0:
                break
            
            # Process each restaurant
            for i in range(num_restaurants):
                try:
                    restaurant_name = restaurant_names[i].text.strip()
                    cuisine = ""
                    neighborhood = ""
                    
                    if i < len(tag_containers):
                        tags = tag_containers[i].find_elements(By.CSS_SELECTOR, "div.Tag_tag__cc4nK")
                        if len(tags) >= 1:
                            cuisine = tags[0].text.strip()
                        if len(tags) >= 2:
                            neighborhood = tags[1].text.strip()
                    
                    all_restaurants.append({
                        'Restaurant': restaurant_name,
                        'Cuisine': cuisine,
                        'Neighborhood': neighborhood
                    })
                    
                    print(f"  {i+1}. {restaurant_name} | {cuisine} | {neighborhood}")
                    
                except Exception as e:
                    print(f"  ✗ Error processing restaurant {i+1}: {str(e)[:50]}")
                    continue
            
            # Move to next page
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                next_button = driver.find_element(By.CSS_SELECTOR, "li.next a")
                parent_li = next_button.find_element(By.XPATH, "..")
                parent_classes = parent_li.get_attribute("class") or ""
                
                if "disabled" in parent_classes:
                    print("\n  ℹ Reached the end")
                    break
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(0.5)
                
                try:
                    next_button.click()
                except:
                    driver.execute_script("arguments[0].click();", next_button)
                
                time.sleep(3)
                
            except Exception as e:
                print(f"\n  ℹ Reached the end")
                break
        
    finally:
        driver.quit()
    
    # Write to CSV
    output_file = 'nyc_restaurant_week.csv'
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Restaurant', 'Cuisine', 'Neighborhood']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for restaurant in all_restaurants:
            writer.writerow(restaurant)
    
    print(f"\n✓ Saved {len(all_restaurants)} restaurants to: {output_file}")
    return output_file


# ============================================================================
# STEP 1.5: MANUAL REVIEW CHECKPOINT
# ============================================================================

def manual_review_checkpoint(csv_file):
    """Pause for manual data review and correction."""
    
    print("\n" + "=" * 80)
    print("MANUAL REVIEW CHECKPOINT")
    print("=" * 80)
    print(f"\nScraping complete! The data has been saved to '{csv_file}'")
    print("\nBefore continuing with API calls, please review the data for any issues.")
    print("\nSteps:")
    print(f"  1. Open '{csv_file}' in Excel or a text editor")
    print("  2. Review and fix any issues you find")
    print("  3. Save the file")
    print("  4. Return here and press Enter to continue")
    
    input("\nPress Enter when ready to continue the pipeline...")
    
    print("✓ Continuing pipeline...")
    
    return csv_file


# ============================================================================
# STEP 2: APPEND ", NEW YORK, NY" TO NEIGHBORHOODS
# ============================================================================

def append_city_to_neighborhoods(input_file):
    """Append ', New York, NY' to all neighborhood values."""
    
    print("\n" + "=" * 80)
    print("STEP 2: APPENDING CITY TO NEIGHBORHOODS")
    print("=" * 80)
    
    df = pd.read_csv(input_file)
    df["Neighborhood"] = df["Neighborhood"].astype(str) + ", New York, NY"
    
    output_file = "nyc_restaurants_nyc.csv"
    df.to_csv(output_file, index=False)
    
    print(f"✓ Appended ', New York, NY' to {len(df)} neighborhoods")
    print(f"✓ Saved to: {output_file}")
    
    return output_file


# ============================================================================
# STEP 3: FETCH ADDRESSES VIA GOOGLE PLACES API
# ============================================================================

def get_address(restaurant, neighborhood, api_key):
    """Get address for a restaurant using Google Places API."""
    
    query = f"{restaurant}, {neighborhood}"
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": query,
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params).json()
        if response["results"]:
            return response["results"][0]["formatted_address"]
    except Exception as e:
        print(f"  ✗ Error fetching address for {restaurant}: {e}")
    
    return None


def fetch_addresses(input_file, api_key):
    """Fetch addresses for all restaurants."""
    
    print("\n" + "=" * 80)
    print("STEP 3: FETCHING ADDRESSES VIA GOOGLE PLACES API")
    print("=" * 80)
    
    df = pd.read_csv(input_file)
    addresses = []
    
    total = len(df)
    for idx, row in df.iterrows():
        print(f"  [{idx+1}/{total}] Fetching address for: {row['Restaurant']}")
        address = get_address(row["Restaurant"], row["Neighborhood"], api_key)
        addresses.append(address)
        time.sleep(0.1)  # Be nice to the API
    
    df["Address"] = addresses
    
    output_file = "restaurants_with_addresses.csv"
    df.to_csv(output_file, index=False)
    
    successful = df["Address"].notna().sum()
    print(f"\n✓ Fetched {successful}/{total} addresses successfully")
    print(f"✓ Saved to: {output_file}")
    
    return output_file


# ============================================================================
# STEP 4: FETCH COORDINATES VIA GOOGLE GEOCODING API
# ============================================================================

def get_coordinates(address, api_key):
    """Get latitude and longitude for an address using Google Geocoding API."""
    
    if pd.isna(address) or not address:
        return None, None
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": address,
        "key": api_key
    }
    
    try:
        response = requests.get(url, params=params).json()
        if response["results"]:
            location = response["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
    except Exception as e:
        print(f"  ✗ Error fetching coordinates for {address}: {e}")
    
    return None, None


def fetch_coordinates(input_file, api_key):
    """Fetch coordinates for all restaurants."""
    
    print("\n" + "=" * 80)
    print("STEP 4: FETCHING COORDINATES VIA GOOGLE GEOCODING API")
    print("=" * 80)
    
    df = pd.read_csv(input_file)
    latitudes = []
    longitudes = []
    
    total = len(df)
    for idx, row in df.iterrows():
        print(f"  [{idx+1}/{total}] Fetching coordinates for: {row['Restaurant']}")
        lat, lng = get_coordinates(row["Address"], api_key)
        latitudes.append(lat)
        longitudes.append(lng)
        time.sleep(0.1)  # Be nice to the API
    
    df["Latitude"] = latitudes
    df["Longitude"] = longitudes
    
    output_file = "restaurants_with_coordinates.csv"
    df.to_csv(output_file, index=False)
    
    successful = df[["Latitude", "Longitude"]].notna().all(axis=1).sum()
    print(f"\n✓ Fetched {successful}/{total} coordinates successfully")
    print(f"✓ Saved to: {output_file}")
    
    return output_file


# ============================================================================
# STEP 5: CONVERT CSV TO JSON
# ============================================================================

def convert_csv_to_json(input_file):
    """Convert CSV file to JSON format for the interactive map."""
    
    print("\n" + "=" * 80)
    print("STEP 5: CONVERTING CSV TO JSON")
    print("=" * 80)
    
    df = pd.read_csv(input_file)
    
    # Drop rows with missing coordinates
    df_clean = df.dropna(subset=["Latitude", "Longitude"])
    
    # Convert to list of dictionaries
    restaurants_list = df_clean.to_dict('records')
    
    output_file = "restaurants.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(restaurants_list, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Converted {len(restaurants_list)} restaurants to JSON")
    print(f"✓ Saved to: {output_file}")
    
    return output_file


# ============================================================================
# STEP 6: GENERATE INTERACTIVE HTML MAP
# ============================================================================

def generate_html_map():
    """Generate the interactive HTML React map."""
    
    print("\n" + "=" * 80)
    print("STEP 6: GENERATING INTERACTIVE HTML MAP")
    print("=" * 80)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NYC Restaurant Week 2026</title>
    
    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.css"/>
    
    <!-- React and Babel -->
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    
    <!-- Leaflet JS -->
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/leaflet.js"></script>
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body, html {
            width: 100%;
            height: 100%;
            overflow: hidden;
            font-family: Arial, sans-serif;
        }
        
        #root {
            width: 100%;
            height: 100%;
        }
        
        /* Desktop styles */
        .filter-panel {
            position: fixed;
            top: 10px;
            left: 60px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            z-index: 9999;
            max-width: 350px;
        }

        .drag-handle {
            display: none; /* Hidden on desktop */
        }

        .desktop-title {
            display: block; /* Visible on desktop */
        }
        
        /* Mobile styles */
        @media (max-width: 768px) {
            .desktop-title {
                display: none !important; /* Hide on mobile */
            }
            .filter-panel {
                position: fixed;
                bottom: 0;
                top: auto;
                left: 0;
                right: 0;
                max-width: none;
                border-radius: 16px 16px 0 0;
                box-shadow: 0 -2px 12px rgba(0,0,0,0.3);
                padding: 0;
                transition: transform 0.3s ease-out;
            }

            .filter-panel.minimized {
                transform: translateY(calc(100% - 100px)); /* Show only header */
            }

            .drag-handle {
                display: block;
                width: 100%;
                padding: 12px;
                text-align: left;
                cursor: grab;
                touch-action: none;
                background: white;
                border-radius: 16px 16px 0 0;
                position: relative;
            }

            .drag-handle:active {
                cursor: grabbing;
            }

            .drag-handle::before {
                content: '';
                display: block;
                width: 40px;
                height: 4px;
                background: #ccc;
                border-radius: 2px;
                margin: 0 auto 8px auto;
            }

            .filter-content {
                padding: 0 15px 20px 15px;
                max-height: calc(60vh - 100px);
                overflow-y: auto;
            }

            .filter-panel h3 {
                font-size: 18px;
                margin-bottom: 0;
            }

            .filter-panel h3 span {
                font-size: 15px;
            }

            .filter-panel label {
                margin: 8px 0 4px 0;
                font-size: 13px;
            }

            .filter-panel select,
            .filter-panel input[type="text"] {
                padding: 10px 8px;
                font-size: 16px; /* Prevents zoom on iOS */
            }

            .filter-panel button {
                padding: 12px;
                margin-top: 8px;
                font-size: 15px;
            }

            .info-text {
                font-size: 11px;
                margin-top: 8px;
                padding-top: 8px;
            }
        }
    </style>
</head>
<body>
    <div id="root"></div>

    <script type="text/babel">
        const { useState, useEffect, useRef } = React;

        function RestaurantMap() {
            const [restaurantsData, setRestaurantsData] = useState([]);
            const [selectedCuisine, setSelectedCuisine] = useState('all');
            const [searchText, setSearchText] = useState('');
            const [filteredRestaurants, setFilteredRestaurants] = useState([]);
            const [map, setMap] = useState(null);
            const [markers, setMarkers] = useState([]);
            const [isMinimized, setIsMinimized] = useState(false);
            const mapContainerRef = useRef(null);
            const panelRef = useRef(null);
            const dragStartY = useRef(0);
            const dragStartMinimized = useRef(false);

            // Load restaurant data from JSON file
            useEffect(() => {
                console.log('Fetching restaurant data...');
                fetch('restaurants.json')
                    .then(response => {
                        console.log('Response received:', response);
                        return response.json();
                    })
                    .then(data => {
                        console.log('Data loaded successfully!');
                        console.log('Number of restaurants:', data.length);
                        console.log('First restaurant:', data[0]);
                        setRestaurantsData(data);
                        setFilteredRestaurants(data);
                    })
                    .catch(error => {
                        console.error('Error loading restaurant data:', error);
                    });
            }, []);

            const cuisines = [...new Set(restaurantsData.map(r => r.Cuisine))].sort();

            // Initialize map
            useEffect(() => {
                if (!mapContainerRef.current || map) return;

                console.log('Initializing map...');
                
                // Detect if mobile device
                const isMobile = window.innerWidth <= 768;
                const initialZoom = isMobile ? 11.5 : 12; // Match Folium map zoom on mobile
                
                console.log('Window width:', window.innerWidth);
                console.log('Is mobile?', isMobile);
                console.log('Initial zoom:', initialZoom);
                
                const mapInstance = L.map(mapContainerRef.current, {
                    center: [40.7429, -73.9803],
                    zoom: initialZoom,
                    zoomControl: true
                });

                L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                    maxZoom: 20
                }).addTo(mapInstance);

                console.log('Map initialized!');
                setMap(mapInstance);

                return () => {
                    if (mapInstance) {
                        mapInstance.remove();
                    }
                };
            }, []);

            // Update markers when filters change
            useEffect(() => {
                console.log('Marker update effect triggered');
                console.log('Map exists?', !!map);
                console.log('Restaurant data length:', restaurantsData.length);
                
                if (!map || restaurantsData.length === 0) {
                    console.log('Returning early - map or data not ready');
                    return;
                }

                const filtered = restaurantsData.filter(restaurant => {
                    const cuisineMatch = selectedCuisine === 'all' || restaurant.Cuisine === selectedCuisine;
                    const searchMatch = searchText === '' || restaurant.Restaurant.toLowerCase().includes(searchText.toLowerCase());
                    return cuisineMatch && searchMatch;
                });

                console.log('Filtered restaurants:', filtered.length);
                console.log('First filtered restaurant:', filtered[0]);
                setFilteredRestaurants(filtered);

                // Clear existing markers
                console.log('Clearing', markers.length, 'existing markers');
                markers.forEach(marker => map.removeLayer(marker));

                // Create new markers
                console.log('Creating markers for', filtered.length, 'restaurants');
                const newMarkers = filtered.map((restaurant, index) => {
                    if (index < 3) {
                        console.log(`Creating marker ${index}:`, restaurant.Restaurant, 'at', restaurant.Latitude, restaurant.Longitude);
                    }
                    
                    const marker = L.marker([restaurant.Latitude, restaurant.Longitude], {
                        icon: L.icon({
                            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
                            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                            iconSize: [25, 41],
                            iconAnchor: [12, 41],
                            popupAnchor: [1, -34],
                            shadowSize: [41, 41]
                        })
                    }).addTo(map);

                    marker.bindTooltip(`
                        <div style="font-family: Arial; font-size: 12px;">
                            <strong>${restaurant.Restaurant}</strong><br>
                            <em>Cuisine:</em> ${restaurant.Cuisine}<br>
                            <em>Address:</em> ${restaurant.Address}
                        </div>
                    `, {
                        permanent: false,
                        direction: 'top',
                        opacity: 0.9
                    });

                    return marker;
                });

                console.log('Created', newMarkers.length, 'markers');
                setMarkers(newMarkers);

                // Fit bounds to markers (only on desktop)
                if (filtered.length > 0) {
                    const isMobile = window.innerWidth <= 768;
                    if (!isMobile) {
                        const bounds = L.latLngBounds(filtered.map(r => [r.Latitude, r.Longitude]));
                        console.log('Fitting map to bounds:', bounds);
                        map.fitBounds(bounds, { padding: [50, 50] });
                    }
                }
            }, [map, selectedCuisine, searchText, restaurantsData]);

            const handleReset = () => {
                setSelectedCuisine('all');
                setSearchText('');
            };

            // Drag handlers for mobile
            const handleDragStart = (e) => {
                const touch = e.touches ? e.touches[0] : e;
                dragStartY.current = touch.clientY;
                dragStartMinimized.current = isMinimized;
            };

            const handleDragMove = (e) => {
                const touch = e.touches ? e.touches[0] : e;
                const deltaY = touch.clientY - dragStartY.current;
                
                // If dragging down and panel is expanded, or dragging up and panel is minimized
                if ((deltaY > 50 && !dragStartMinimized.current) || (deltaY < -50 && dragStartMinimized.current)) {
                    setIsMinimized(!dragStartMinimized.current);
                    dragStartY.current = touch.clientY;
                    dragStartMinimized.current = !dragStartMinimized.current;
                }
            };

            const handleDragEnd = () => {
                // Reset drag tracking
                dragStartY.current = 0;
            };

            const toggleMinimize = () => {
                setIsMinimized(!isMinimized);
            };

            return (
                <div style={{ width: '100%', height: '100%', position: 'relative' }}>
                    <div
                        ref={mapContainerRef}
                        style={{
                            position: 'absolute',
                            top: 0,
                            bottom: 0,
                            left: 0,
                            right: 0
                        }}
                    />

                    <div 
                        ref={panelRef}
                        className={`filter-panel ${isMinimized ? 'minimized' : ''}`}
                    >
                        <div 
                            className="drag-handle"
                            onTouchStart={handleDragStart}
                            onTouchMove={handleDragMove}
                            onTouchEnd={handleDragEnd}
                            onMouseDown={handleDragStart}
                            onMouseMove={handleDragMove}
                            onMouseUp={handleDragEnd}
                            onClick={toggleMinimize}
                        >
                            <h3 style={{ margin: '0', fontSize: '18px', color: '#333' }}>
                                <strong>NYC Restaurant Week 2026</strong><br />
                                <span style={{ fontSize: '15px', fontWeight: 'normal' }}>Jan. 20th - Feb. 12th</span>
                            </h3>
                        </div>

                        <div className="filter-content" style={{ padding: '15px' }}>
                            <h3 style={{ margin: '0 0 10px 0', fontSize: '20px', color: '#333', display: 'block' }} className="desktop-title">
                                <strong>NYC Restaurant Week 2026</strong><br />
                                <span style={{ fontSize: '16px', fontWeight: 'normal' }}>Jan. 20th - Feb. 12th</span>
                            </h3>
                            <label style={{ display: 'block', margin: '10px 0 5px 0', fontWeight: 'bold', fontSize: '14px' }}>
                                Filter by Cuisine:
                            </label>
                            <select
                                value={selectedCuisine}
                                onChange={(e) => setSelectedCuisine(e.target.value)}
                                style={{
                                    width: '100%',
                                    padding: '8px',
                                    border: '1px solid #ddd',
                                    borderRadius: '4px',
                                    fontSize: '14px'
                                }}
                            >
                                <option value="all">All Cuisines</option>
                                {cuisines.map(cuisine => (
                                    <option key={cuisine} value={cuisine}>{cuisine}</option>
                                ))}
                            </select>

                            <label style={{ display: 'block', margin: '10px 0 5px 0', fontWeight: 'bold', fontSize: '14px' }}>
                                Search Restaurant:
                            </label>
                            <input
                                type="text"
                                value={searchText}
                                onChange={(e) => setSearchText(e.target.value)}
                                placeholder="Type restaurant name..."
                                style={{
                                    width: '100%',
                                    padding: '8px',
                                    border: '1px solid #ddd',
                                    borderRadius: '4px',
                                    fontSize: '14px'
                                }}
                            />

                            <button
                                onClick={handleReset}
                                style={{
                                    width: '100%',
                                    padding: '10px',
                                    marginTop: '10px',
                                    background: '#64B5F6',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '4px',
                                    cursor: 'pointer',
                                    fontSize: '14px',
                                    fontWeight: 'bold'
                                }}
                            >
                                Reset Filters
                            </button>

                            <div className="info-text" style={{
                                fontSize: '12px',
                                color: '#666',
                                marginTop: '10px',
                                paddingTop: '10px',
                                borderTop: '1px solid #eee'
                            }}>
                                Showing <strong style={{ color: '#2196F3' }}>{filteredRestaurants.length}</strong> restaurants
                            </div>
                        </div>
                    </div>
                </div>
            );
        }

        ReactDOM.render(<RestaurantMap />, document.getElementById('root'));
    </script>
</body>
</html>'''
    
    output_file = "restaurant_map.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Generated interactive HTML map")
    print(f"✓ Saved to: {output_file}")
    print(f"\nTo view the map:")
    print(f"  1. Make sure 'restaurants.json' is in the same directory")
    print(f"  2. Open '{output_file}' in a web browser")
    
    return output_file


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_pipeline(api_key=None):
    """Run the complete pipeline."""
    
    print("\n" + "=" * 80)
    print("NYC RESTAURANT WEEK DATA PIPELINE")
    print("=" * 80)
    print("\nThis pipeline will:")
    print("1. Scrape restaurant data from NYC Tourism website")
    print("2. Pause for manual data review and corrections")
    print("3. Append ', New York, NY' to neighborhoods")
    print("4. Fetch addresses via Google Places API")
    print("5. Fetch coordinates via Google Geocoding API")
    print("6. Convert final data to JSON for the interactive map")
    print("7. Generate interactive HTML map with React")
    print("\n" + "=" * 80)
    
    # Check if API key is provided
    if not api_key or api_key == "YOUR_GOOGLE_API_KEY_HERE":
        print("\n⚠ WARNING: No Google API key provided!")
        print("Steps 4 and 5 (address and coordinate fetching) will be skipped.")
        print("To enable these steps, set API_KEY variable or pass it to run_pipeline()")
        use_api = False
    else:
        use_api = True
    
    try:
        # Step 1: Scrape data
        csv_file = scrape_restaurant_week()
        
        # Step 1.5: Manual review checkpoint
        csv_file = manual_review_checkpoint(csv_file)
        
        # Step 2: Append city to neighborhoods
        csv_file = append_city_to_neighborhoods(csv_file)
        
        if use_api:
            # Step 3: Fetch addresses
            csv_file = fetch_addresses(csv_file, api_key)
            
            # Step 4: Fetch coordinates
            csv_file = fetch_coordinates(csv_file, api_key)
        else:
            print("\n⚠ Skipping API steps (no API key provided)")
        
        # Step 5: Convert to JSON
        json_file = convert_csv_to_json(csv_file)
        
        # Step 6: Generate HTML map
        html_file = generate_html_map()
        
        print("\n" + "=" * 80)
        print("✓ PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print(f"\nFinal outputs:")
        print(f"  - Data file: {json_file}")
        print(f"  - Interactive map: {html_file}")
        print(f"\nTo view your interactive map:")
        print(f"  1. Open '{html_file}' in a web browser")
        print(f"  2. Make sure '{json_file}' is in the same directory")
        
    except KeyboardInterrupt:
        print("\n\n✗ Pipeline interrupted by user")
    except Exception as e:
        print(f"\n✗ Pipeline failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the complete pipeline
    # Replace API_KEY at the top of this file with your actual Google API key
    run_pipeline(api_key=API_KEY)
