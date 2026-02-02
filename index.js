const { useState, useEffect, useRef } = React;

function RestaurantMap() {
    const [restaurantsData, setRestaurantsData] = useState([]);
    const [selectedCuisine, setSelectedCuisine] = useState('all');
    const [searchText, setSearchText] = useState('');
    const [filteredRestaurants, setFilteredRestaurants] = useState([]);
    const [map, setMap] = useState(null);
    const [markers, setMarkers] = useState([]);
    const mapContainerRef = useRef(null);

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
                console.log('Sample cuisines:', data.slice(0, 5).map(r => r.Cuisine));
                setRestaurantsData(data);
                setFilteredRestaurants(data);
            })
            .catch(error => {
                console.error('Error loading restaurant data:', error);
            });
    }, []);

    const cuisines = [...new Set(restaurantsData.map(r => r.Cuisine))].sort();
    console.log('Unique cuisines:', cuisines);

    // Initialize map
    useEffect(() => {
        if (!mapContainerRef.current || map) return;

        console.log('Initializing map...');
        const mapInstance = L.map(mapContainerRef.current, {
            center: [40.7429, -73.9803],
            zoom: 12,
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

        // Fit bounds to markers
        if (filtered.length > 0) {
            const bounds = L.latLngBounds(filtered.map(r => [r.Latitude, r.Longitude]));
            console.log('Fitting map to bounds:', bounds);
            map.fitBounds(bounds, { padding: [50, 50] });
        }
    }, [map, selectedCuisine, searchText, restaurantsData]);

    const handleReset = () => {
        setSelectedCuisine('all');
        setSearchText('');
    };

    return (
        <div style={{ width: '100%', height: '100%', position: 'relative' }}>
            <div
                ref={mapContainerRef}
                className="map-container"
            />

            <div className="filter-panel">
                <h3>
                    <strong>NYC Restaurant Week 2026</strong><br />
                    <span>Jan. 20th - Feb. 12th</span>
                </h3>

                <label htmlFor="cuisine-select">
                    Filter by Cuisine:
                </label>
                <select
                    id="cuisine-select"
                    value={selectedCuisine}
                    onChange={(e) => setSelectedCuisine(e.target.value)}
                >
                    <option value="all">All Cuisines</option>
                    {cuisines.map(cuisine => (
                        <option key={cuisine} value={cuisine}>{cuisine}</option>
                    ))}
                </select>

                <label htmlFor="search-input">
                    Search Restaurant:
                </label>
                <input
                    type="text"
                    id="search-input"
                    value={searchText}
                    onChange={(e) => setSearchText(e.target.value)}
                    placeholder="Type restaurant name..."
                />

                <button
                    onClick={handleReset}
                    className="reset-button"
                >
                    Reset Filters
                </button>

                <div className="info-text">
                    Showing <strong>{filteredRestaurants.length}</strong> restaurants
                </div>
            </div>
        </div>
    );
}

// Render the app
ReactDOM.render(<RestaurantMap />, document.getElementById('root'));
