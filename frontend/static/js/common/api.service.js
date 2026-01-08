const getCookie = (name) => {
    const cookieString = document.cookie || "";
    const cookies = cookieString.split(";").map((cookie) => cookie.trim());
    for (const cookie of cookies) {
        if (cookie.startsWith(`${name}=`)) {
            return decodeURIComponent(cookie.split("=")[1]);
        }
    }
    return "";
};

const ClubApi = {
    post(href, callback) {
        const csrfToken = getCookie("csrftoken");
        const params = {
            method: "POST",
            credentials: "include",
            headers: {
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest",
            },
        };

        fetch(href + "?is_ajax=true", params)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => callback(data))
            .catch((error) => {
                callback({ error: error.message });
            });
    },

    get(href, callback) {
        const params = {
            method: "GET",
            credentials: "include",
        };

        fetch(href + "?is_ajax=true", params)
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => callback(data))
            .catch((error) => {
                callback({ error: error.message });
            });
    },
};

export default ClubApi;
