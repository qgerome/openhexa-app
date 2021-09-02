function QuickSearch(advancedSearchUrl) {
    const MODE_WAITING_FOR_INPUT = 'MODE_WAITING_FOR_INPUT';
    const MODE_BUSY = 'MODE_BUSY';
    const MODE_NO_RESULTS = 'MODE_NO_RESULTS';
    const MODE_RESULTS = 'MODE_RESULTS';

    let abortController = null;

    return {
        MODE_BUSY,
        MODE_RESULTS,
        MODE_NO_RESULTS,
        MODE_WAITING_FOR_INPUT,
        expanded: false,
        query: "",
        mode: MODE_WAITING_FOR_INPUT,
        results: [],
        expand() {
            this.expanded = true;
            bodyScrollLock.disableBodyScroll(this.$refs.modalContent);
            setTimeout(() => this.$refs.input.focus(), 100);
        },
        collapse() {
            this.expanded = false
            bodyScrollLock.enableBodyScroll(this.$refs.modalContent);
        },
        toggle() {
            this.expanded ? this.collapse() : this.expand()
        },
        switchToAdvancedSearch($event) {
            $event.preventDefault();
            window.location.href = `${advancedSearchUrl}?query=${this.query}`;
        },
        async check() {
            if (this.query.length >= 3) {
                await this.submit();
            } else {
                this.waitForInput();
            }
        },
        async submit() {
            if (abortController !== null) {
                abortController.abort();
            }
            abortController = new AbortController();
            this.mode = MODE_BUSY;
            this.results = [];
            try {
                const response = await fetch(`${this.$refs.form.action}?query=${this.query}`, {
                    method: this.$refs.form.method,
                    headers: {'Content-Type': 'application/json'},
                    signal: abortController.signal
                });
                const responeData = await response.json();
                this.results = responeData.results;
                const newMode = this.results.length > 0 ? MODE_RESULTS : MODE_NO_RESULTS;
                this.mode = newMode;
                abortController = null;
            } catch (e) {
                if (e.message.includes("abort")) {
                    console.info("Aborting")
                } else {
                    console.error(`Error while submitting search: ${e}`);
                }
            }
        },
        waitForInput() {
            console.log(`Waiting for input`);

            this.mode = MODE_WAITING_FOR_INPUT;
            this.results = [];
        },
    }
}

/**
 * Auto Refresh component
 * @param url
 * @param delay (in seconds)
 * @returns {{init(*): void, submit(): Promise<void>, interval: null, refreshedHtml: null}}
 * @constructor
 */
function AutoRefresh(url, delay) {
    return {
        interval: null,
        refreshedHtml: null,
        init($el) {
            this.refreshedHtml = $el.innerHTML;
            this.interval = setInterval(this.submit.bind(this), delay * 1000);
        },
        async submit() {
            try {
                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        "Accepts": "text/html",
                        "X-CSRFToken": document.cookie
                            .split('; ')
                            .find(row => row.startsWith('csrftoken='))
                            .split('=')[1]
                    },
                });
                this.refreshedHtml = await response.text();
            } catch (e) {
                console.error(`Error while submitting form: ${e}`);
            } finally {
                clearInterval(this.interval);
            }
        },
    }
}

/**
 * Updatable component
 * @param url
 * @returns {{init(*): void, submit(): Promise<void>, interval: null, refreshedHtml: null}}
 * @constructor
 */
function Updatable(url) {
    console.log(`Creating Updatable (url: ${url})`);

    return {
        editing: [],
        updates: {},
        updated: false,
        update(key, value) {
            this.updates[key] = value;
            this.updated = true;
        },
        async submit() {
            try {
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": document.cookie
                            .split('; ')
                            .find(row => row.startsWith('csrftoken='))
                            .split('=')[1]
                    },
                    body: JSON.stringify(this.updates)
                });
                this.$el.innerHTML = await response.text();
                this.updated = false;
            } catch (e) {
                console.error(`Error while submitting form: ${e}`);
            }
        },
    }
}

/**
 * Editable component
 *
 * @param key
 * @param value
 * @param originalValue
 * @returns {{isChanged(): *, displayedValue(): *|string, originalValue, toggle(): void, value: *, key, editing: boolean}|boolean|*|string}
 * @constructor
 */
function Editable(key, value, originalValue) {
    return {
        key,
        // TODO: check
        // value,
        value: value !== "" ? value : originalValue,
        originalValue,
        editing: false,
        isChanged() {
            return this.value !== "" && this.value !== originalValue;
        },
        displayedValue() {
            return this.value !== "" ?
                this.value :
                (originalValue !== "" ? originalValue : "-");
        },
        toggle() {
            this.editing = !this.editing;
            if (this.editing) {
                setTimeout(() => {
                    this.$refs.input.focus();
                    this.$refs.input.setSelectionRange(10000, 10000);
                }, 100)
            }
        },
    }
}

/**
 * Commentable component
 *
 * @param url
 * @param contentTypeKey
 * @param objectId
 * @returns {{cancel(*): void, submit(*): Promise<void>, startCommenting(*): void, text: string, commenting: boolean}}
 * @constructor
 */
function Commentable(url, contentTypeKey, objectId) {
    console.log(`Creating Commentable (url: ${url}, contentTypeKey: ${contentTypeKey}, objectId: ${objectId})`);

    return {
        text: "",
        commenting: false,
        startCommenting($event) {
            this.commenting = $event.target.value !== "";
        },
        cancel($event) {
            this.text = "";
            this.commenting = false;
            $event.target.blur();
        },
        async submit($event) {
            $event.preventDefault();
            try {
                let formData = new FormData();
                formData.append("text", this.text);
                formData.append("content_type_key", contentTypeKey);
                formData.append("object_id", objectId);

                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        "X-CSRFToken": document.cookie
                            .split('; ')
                            .find(row => row.startsWith('csrftoken='))
                            .split('=')[1]
                    },
                    body: formData
                });
                const responseText = await response.text();
                const newContent = document.createElement("div");
                newContent.innerHTML = responseText;
                this.$refs['form-container'].after(newContent.querySelector("li"));
                this.text = "";
                $event.target.blur();
            } catch (e) {
                console.error(`Error while submitting form: ${e}`);
            }
        },
    }
}