## Steps
1. Load Restaurants from  "Hi vull anar"
1. google maps SDK `find_place` by name to get **place_id**
1. Get more information of the place with google maps SDK `place`
    - Fields:
        * place_id
        * name
        * international_phone_number
        * formatted_address
        * formatted_phone_number
        * website
        * url
        * business_status
        * current_opening_hours -> weekday_text
        * editorial_summary
            - language
            - overview
        * geometry
            - location
                * lat
                * lng
        * price_level
        * rating
        * types
        * reservable
        * delivery
        * dine_in
        * user_ratings_total
        * wheelchair_accessible_entrance
        * serves_beer
        * serves_wine
        * serves_breakfast
        * serves_brunch
        * serves_lunch
        * serves_dinner
        * serves_vegetarian_food
        * takeout
        * reviews

['website', 'photo', 'business_status', 'opening_hours', 'plus_code', 'rating', 'geometry/location', 'user_ratings_total', 'serves_wine', 'geometry/viewport/southwest/lat', 'geometry/viewport/southwest/lng', 'takeout', 'icon', 'review', 'geometry/viewport', 'formatted_address', 'serves_beer', 'name', 'reviews', 'delivery', 'price_level', 'serves_lunch', 'geometry/location/lat', 'geometry/viewport/northeast/lng', 'permanently_closed', 'serves_vegetarian_food', 'url', 'address_component', 'serves_dinner', 'reservable', 'geometry/viewport/southwest', 'utc_offset', 'geometry/viewport/northeast', 'serves_brunch', 'dine_in', 'vicinity', 'geometry/location/lng', 'serves_breakfast', 'type', 'wheelchair_accessible_entrance', 'geometry/viewport/northeast/lat', 'curbside_pickup', 'adr_address', 'current_opening_hours', 'international_phone_number', 'secondary_opening_hours', 'geometry', 'place_id', 'formatted_phone_number', 'editorial_summary']


## Next steps
- [X] re-run `GoogleMapsAPI.get_places()` to get reviews and check why we are not getting `type`.
- [X] take more place info from reviews 
- [] get info from webpage
- [] embedding this info? summry first? categories?
