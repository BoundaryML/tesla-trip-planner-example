class CityState {
    city string
    state string
}

class ZipCode {
    zip_code string
}

type Location = CityState | ZipCode

class Trip {
    name string
    start Location
    end Location
    type "business" | "personal"
    stops Stop[]
}

class Stop {
    type "charging" | "overnight"
    location Location
    reason string @description(#"
        why this stop is recommended
    "#)
}

function GetTrip(message: string) -> Trip {
    client "openai/gpt-4o"
    prompt #"
        {{ ctx.output_format }}

        {{ _.role('user') }}
        {{ message }}
    "#
}


test TestName {
  functions [GetTrip]
  args {
    message #"
        Create a route from columbus, ohio to Seattle via Dallas, TX for my trip in Tesla Model Y with stop every 200 miles for charging and food. Also, stop around 5 pm to rest for about 10 hours every evening. Show accommodations including RV PARKS that allow charging and camping in Tesla for the night stay.
    "#
  }
}
