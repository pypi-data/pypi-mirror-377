import { writable, get } from "svelte/store";
import Widget from "./components/Widget.svelte";
const defaultWidgetState = {
    states: [],
    urls: [],
    type: "image",
    message: "",
    config: { image: [], regions: [] },
    labels: { image: {}, polygons: [], masks: [], boxes: [] },
    action: "",
    preload: [],
    maxCanvasSize: 512,
    maxViewHeight: 512,
    idx: 0,
    viewState: "labeling",
    indexState: {
        rows: [],
        columns: [],
        rowsPerPage: 5,
        rowCount: 0,
        sortModel: [],
        filterModel: [],
        page: 1,
    },
    buttons: {
        next: true,
        prev: true,
        save: true,
        config: true,
        delete: true,
        ignore: true,
        unignore: true,
    },
    base: {
        serverRoot: "",
        url: "",
    },
    progress: -1,
    mode: "light",
};
const buildAttributeStoreFactory = (initializer) => {
    const stores = {};
    const destructors = {};
    let pystamp = null;
    const inner = (name) => {
        let store = writable(null);
        let external = initializer(name, (value) => {
            if (value != get(store)) {
                // console.log(`Setting ${name} to ${value}.`);
                pystamp = Date.now();
                store.set(value);
            }
        });
        const set = (value, force) => {
            if (force || (pystamp && Date.now() - pystamp > 500)) {
                store.set(value);
                external.set(value);
            }
        };
        destructors[name] = external.destroy;
        return {
            set,
            update: (updater) => set(updater(get(store))),
            subscribe: store.subscribe,
        };
    };
    return {
        extract: (name) => {
            if (!stores[name]) {
                stores[name] = inner(name);
            }
            return stores[name];
        },
        destroy: () => {
            Object.values(destructors).map((d) => d());
        },
    };
};
export default Widget;
export { buildAttributeStoreFactory, defaultWidgetState };
