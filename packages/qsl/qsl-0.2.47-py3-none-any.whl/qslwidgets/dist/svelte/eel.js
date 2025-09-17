import Widget, { defaultWidgetState, buildAttributeStoreFactory, } from "./widget";
window.eel.set_host("ws://localhost:8080");
const buildModelStateExtractor = () => {
    return buildAttributeStoreFactory((name, set) => {
        const syncKey = `sync:${name}`;
        const sync = (event) => set(event.detail.value);
        window.eel.init(name)(set);
        document.addEventListener(syncKey, sync, false);
        return {
            set: (value) => window.eel.sync(name, value)(),
            destroy: () => document.removeEventListener(syncKey, sync, false),
        };
    });
};
const pysync = (key, value) => {
    document.dispatchEvent(new CustomEvent(`sync:${key}`, {
        detail: { value },
    }));
};
window.eel.expose(pysync, "sync");
new Widget({
    target: document.getElementById("root"),
    props: { extract: buildModelStateExtractor().extract },
});
