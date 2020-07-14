$(function () {

    const request = new XMLHttpRequest()
    request.open('GET', '/search.json', true)

    request.onload = function () {
        if (this.status >= 200 && this.status < 400) {

            const documents = JSON.parse(this.response)
            const documentsByURI = {}

            const index_fr = lunr(function () {
                this.use(lunr.fr)
                this.ref('uri')
                this.field('title')
                this.field('content')
                this.metadataWhitelist = ['position']

                documents.forEach(function (doc) {
                    this.add(doc)
                    documentsByURI[doc.uri] = doc
                }, this)
            })

            const searchField = document.getElementById("search-field")
            const searchMessage = document.getElementById("search-message")
            const searchResults = document.getElementById("search-results")

            searchField.addEventListener("keyup", function () {

                const query = searchField.value

                if (query.length > 2) {
                    const results = index_fr.search(query)

                    if (results.length > 0) {
                        searchMessage.innerHTML = `<p><b>${results.length}</b> résultats trouvés pour <b>${query}</b>.</p>`

                        searchResults.innerHTML = results.map(result => {
                            return `<li><a href="${result.ref}">${documentsByURI[result.ref].title}</a></li>`
                        }).join("\n")
                        // searchResults
                    } else {
                        searchMessage.innerHTML = `<p>Aucun résultat pour <b>${query}</b>.</p>`
                    }
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