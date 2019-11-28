const buildFormElement = () => {
    // Create label
    // Create input
    // Define input type: boolean, integer, float
    // https://www.w3schools.com/tags/tag_input.asp
    // Set value to current value
    // Add element to DOM

}

const getFormElementType = (attribute) => {
    let formElementType
    switch (attribute) {
        case "use_humidity":
        case "display_host_ip":
        case "display_sleep_timer":
        case "display_debug_panel":
            formElementType = "boolean"
            break;

        case "sleep_timeout_sec":
        case "ambient_temp_delay":
            formElementType = "integer"
            break;

        case "screen_max_frame_rate":
            formElementType = "float"

        default:
            console.warn("Invalid form element type!", configElement);
            break;
    }

    return formElementType
}

const loadConfigToForm = (response) => {
    const configObject = JSON.parse(response);
    console.log("Starting form construct loop through response");
    for (const attribute in configObject) {
        if (configObject.hasOwnProperty(attribute)) {
            const value = configObject[attribute];
            console.log("Building form element for:", attribute);
            const formElementType = getFormElementType(attribute)
            buildFormElement(attribute, value, formElementType)
        }
    }

    if (Object.keys(configObject).length > 0) {
        console.warn("ADD SAVE BUTTON WHEN THERE IS AN ATTRIBUTE TO EDIT");
        
    } else {
        console.warn("No attributes are returned to edit!");
    }

}

const getCurrentConfig = (configGetUrl) => {
    console.log("Building config fetch");
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = () => {
        if (this.readyState == 4 && this.status == 200) {
            console.log("Succesfull response:");
            console.log(xhttp.response);
            loadConfigToForm(response)
        }
    };
    xhttp.open("GET", configGetUrl, true);
    xhttp.send();
    console.log("Fetching config from Smart Mirror...");
}

const main = () => {
    console.log("Page has loaded");
    const configGetUrl = "/config"
    getCurrentConfig(configGetUrl)
}

window.addEventListener("load", main)