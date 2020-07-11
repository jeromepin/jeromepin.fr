$(function () {

    const request = new XMLHttpRequest();
    request.open('GET', '/index.json', true);

    request.onload = function () {
        if (this.status >= 200 && this.status < 400) {
            const fr_index = new FlexSearch({
                doc: {
                    id: "id",
                    field: [
                        "title",
                        "date",
                        "content"
                    ]
                }
            });

            const documents = JSON.parse(this.response);

            for (let index = 0; index < documents.length; index++) {
                const document = documents[index];
                // console.log(document)
                fr_index.add(document.id, document);

            }

            const searchField = document.getElementById("search");
            searchField.addEventListener("keyup", function () {
                const query = searchField.value;
                if (query.length > 2) {
                    const results = fr_index.search(query, 10);
                    console.log(results)
                }
            })

        } else {
            // We reached our target server, but it returned an error
        }
    };

    request.onerror = function () {
        // There was a connection error of some sort
    };

    request.send();
});