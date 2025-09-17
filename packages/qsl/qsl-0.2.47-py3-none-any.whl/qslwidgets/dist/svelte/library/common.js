import { readable, get } from "svelte/store";
import { getStores } from "./instanceStores.js";
import { bmp2rle, rle2bmp } from "./masking.js";
export const pct2css = (pct) => `${100 * pct}%`;
export const insertOrAppend = (arr, item, idx, save) => (save ? [item] : []).concat(arr
    .slice(0, idx > -1 ? idx : undefined)
    .concat(idx > -1 ? arr.slice(idx + 1) : []));
export const copy = (o) => {
    try {
        return JSON.parse(JSON.stringify(o));
    }
    catch (_a) {
        throw `Failed to copy object: ${o}`;
    }
};
export const labels2string = (labels) => {
    return Object.keys(labels)
        .filter((k) => labels[k].length == 1)
        .map((k) => `${k}: ${labels[k][0]}`)
        .join(", ");
};
export const epsilon = 1e-4;
export const labels2draft = (labels) => {
    return {
        image: copy((labels === null || labels === void 0 ? void 0 : labels.image) || {}),
        polygons: copy((labels === null || labels === void 0 ? void 0 : labels.polygons) || []),
        masks: ((labels === null || labels === void 0 ? void 0 : labels.masks) || []).map((m) => {
            return Object.assign(Object.assign({}, m), { map: rle2bmp(m.map) });
        }),
        dimensions: (labels === null || labels === void 0 ? void 0 : labels.dimensions) ? copy(labels.dimensions) : undefined,
        boxes: copy((labels === null || labels === void 0 ? void 0 : labels.boxes) || []),
    };
};
export const sortBoxPoints = (box) => {
    const pt1 = box.pt1;
    const pt2 = box.pt2 || box.pt1;
    return Object.assign(Object.assign({}, box), { pt1: {
            x: Math.min(pt1.x, pt2.x),
            y: Math.min(pt1.y, pt2.y),
        }, pt2: {
            x: Math.max(pt1.x, pt2.x),
            y: Math.max(pt1.y, pt2.y),
        } });
};
export const draft2labels = (labels) => {
    return Object.assign(Object.assign({}, labels), { boxes: labels.boxes.map(sortBoxPoints), masks: labels.masks.map((m) => {
            return Object.assign(Object.assign({}, m), { map: bmp2rle(m.map) });
        }) });
};
export const insertOrAppendByTimestamp = (current, existing) => {
    return insertOrAppend(existing, current, existing.findIndex((i) => i.timestamp === current.timestamp), true).sort((a, b) => (a.timestamp > b.timestamp ? 1 : -1));
};
export const shortcutify = (initial) => {
    let taken = initial.reduce((memo, entry) => entry.options
        ? memo.concat(entry.options
            .filter((o) => o.shortcut)
            .map((o) => o.shortcut))
        : memo, []);
    return initial.map((entry) => {
        return Object.assign(Object.assign({}, entry), { options: entry.options
                ? entry.options.map((option) => {
                    let shortcut = option.shortcut;
                    if (!shortcut) {
                        shortcut = [...option.name.toLowerCase()].find((c) => taken.indexOf(c) == -1);
                        if (shortcut) {
                            taken.push(shortcut);
                        }
                    }
                    return Object.assign(Object.assign({}, option), { shortcut });
                })
                : undefined });
    });
};
export const computeDefaultRegionLabels = (config) => {
    return config.regions
        ? Object.fromEntries(config.regions.map((r) => [r.name, r.defaults || []]))
        : {};
};
export const renderBitmapToCanvas = (bitmap, canvas, color) => {
    if (!canvas) {
        return false;
    }
    let context = canvas.getContext("2d");
    if (context && bitmap) {
        const dimensions = bitmap.dimensions();
        canvas.width = dimensions.width;
        canvas.height = dimensions.height;
        const pixels = context.createImageData(dimensions.width, dimensions.height);
        const blankValues = [0, 0, 0, 0];
        const colorValues = color === "red"
            ? [255, 0, 0, 127]
            : color === "blue"
                ? [0, 0, 255, 127]
                : [255, 255, 0, 127];
        bitmap
            .contents()
            .forEach((v, i) => pixels.data.set(v === 255 ? colorValues : blankValues, i * 4));
        context.putImageData(pixels, 0, 0);
        return true;
    }
    return false;
};
export const buildOptions = (selected, config) => config.options || config.multiple
    ? (config.options || [])
        .concat(selected
        ? selected
            .filter((s) => (config.options || []).findIndex((o) => o.name === s) == -1)
            .map((s) => {
            return { name: s, shortcut: "" };
        })
        : [])
        .map((o) => {
        return Object.assign(Object.assign({}, o), { selected: selected && selected.indexOf(o.name) > -1, shortcut: o.shortcut || "", label: `${o.displayName || o.name} ${o.shortcut ? `(${o.shortcut})` : ""}` });
    })
    : undefined;
export const delay = (amount) => new Promise((resolve) => setTimeout(resolve, amount));
export const simulateClick = (target, offset) => new Promise((resolve) => {
    if (!target)
        return;
    target.focus({ preventScroll: true });
    target.classList.add("active");
    const { x, y } = target.getBoundingClientRect();
    const args = Object.assign({ bubbles: true, cancelable: true }, (offset
        ? {
            clientX: x + offset.x,
            clientY: y + offset.y,
        }
        : {}));
    target.dispatchEvent(new MouseEvent("mousedown", args));
    target.dispatchEvent(new MouseEvent("mouseup", args));
    delay(100).then(() => {
        target.dispatchEvent(new MouseEvent("click", args));
        target.classList.remove("active");
        target.blur();
        resolve();
    });
});
export const findFocusTarget = (element) => element.closest(".qslwidgets-labeler");
export const elementIsFocused = (element, target) => {
    const active = document.activeElement;
    if (!active) {
        return false;
    }
    const parent1 = findFocusTarget(active);
    const parent2 = findFocusTarget(element);
    if (!parent1 || !parent2) {
        return false;
    }
    if (target &&
        target instanceof HTMLElement &&
        (target.nodeName === "TEXTAREA" ||
            (target.nodeName === "INPUT" &&
                target.type == "text"))) {
        // We're typing into a form field and this field is *not* a checkbox
        // or radio element.
        return false;
    }
    const same = parent1.isSameNode(parent2);
    return same;
};
export const focus = (element) => {
    if (!element)
        return false;
    const parent = findFocusTarget(element);
    if (!parent) {
        return false;
    }
    const target = parent.querySelector(".focus-target");
    if (!target) {
        return false;
    }
    target.focus({ preventScroll: true });
    return true;
};
export const processSelectionChange = (value, selected, multiple, required, options) => selected && selected.indexOf(value) > -1
    ? multiple
        ? selected.filter((v) => v != value)
        : required
            ? selected
            : options
                ? []
                : [value]
    : multiple
        ? (selected || []).concat([value])
        : [value];
export const createContentLoader = (options) => {
    let state = {
        targets: options.targets,
        loadState: (options.targets.every((t) => t === undefined)
            ? "empty"
            : "loading"),
        mediaState: undefined,
    };
    let interim = options.targets.map(() => undefined);
    let apply;
    const promise = new Promise((resolve, reject) => (apply = { reject, resolve }));
    const stores = getStores();
    return {
        callbacks: options.targets.map((target, targeti) => ({
            load: (event) => options.load(event, target).then((mediaState) => {
                interim[targeti] = mediaState;
                if (interim.every((i) => i !== undefined)) {
                    apply.resolve(Object.assign(Object.assign({}, state), { loadState: "loaded", mediaState: { states: interim } }));
                }
            }, () => apply.reject(target)),
            error: () => apply.reject(target),
        })),
        promise,
        state: readable(state, (set) => {
            promise.then(set, (t) => {
                set(Object.assign(Object.assign({}, state), { loadState: "error" }));
                stores.toast.push(`An error occurred loading ${t}.`, {
                    theme: {
                        "--toastBackground": "var(--color3)",
                        "--toastBarBackground": "#C53030",
                    },
                });
            });
        }),
    };
};
export const undoable = (initial, serialize, deserialize, destroy, length = 10, debounce = 500) => {
    let count = 0;
    let subscribers = {
        state: {},
        history: {},
    };
    let history = [];
    let current = initial;
    const notify = () => {
        Object.values(subscribers["state"]).forEach((subscriber) => {
            subscriber(current);
        });
        Object.values(subscribers["history"]).forEach((subscriber) => subscriber(history.length));
    };
    let lastSnapshotTime = Date.now();
    return {
        history: {
            undo: () => {
                if (history.length > 0) {
                    current = history.pop();
                    if (deserialize) {
                        current = deserialize(current);
                    }
                    notify();
                }
            },
            subscribe: (subscriber) => {
                subscribers["history"][count] = subscriber;
                subscriber(history.length);
                count = count + 1;
                return () => delete subscribers["history"][count - 1];
            },
        },
        state: {
            set: (update) => {
                current = update;
                notify();
            },
            snapshot: () => {
                const nextSnapshotTime = Date.now();
                let nextSnapshot = (serialize || structuredClone)(current);
                let remove;
                // Debounce should not apply to the first item, since it's likely our "initial state"
                // and we do not want to overwrite it.
                if (nextSnapshotTime - lastSnapshotTime > debounce ||
                    history.length == 1) {
                    // Get as many items as needed from the front of the array.
                    remove = history.slice(0, -(length - 1));
                    history = [...history.slice(-(length - 1)), nextSnapshot];
                }
                else {
                    // Get the last item from the array, since we're just going
                    // to treat that last snapshot as redundant.
                    remove = history.slice(-1);
                    history = [...history.slice(0, -1), nextSnapshot];
                }
                if (destroy) {
                    destroy(remove, history);
                }
                lastSnapshotTime = nextSnapshotTime;
            },
            reset: (update) => {
                if (destroy) {
                    destroy(history, [update]);
                }
                history = [];
                current = update;
                notify();
            },
            subscribe: (subscriber) => {
                subscribers["state"][count] = subscriber;
                subscriber(current);
                count = count + 1;
                return () => delete subscribers["state"][count - 1];
            },
        },
    };
};
export const emptyDraftState = {
    drawing: {
        mode: "boxes",
        radius: 5,
        threshold: -1,
    },
    dirty: false,
    labels: { image: {}, polygons: [], boxes: [], masks: [] },
    image: null,
};
const deallocateMaps = (remove, keep) => {
    const [removeMaps, keepMaps] = [remove, keep].map((stateSet) => stateSet
        .map((state) => state.labels.masks
        .map((m) => m.map)
        .concat(state.drawing.active && state.drawing.mode === "masks"
        ? [state.drawing.active.region.map]
        : []))
        .flat());
    const maps = new Set(removeMaps.filter((m) => keepMaps.indexOf(m) == -1));
    maps.forEach((m) => m.free());
};
export const createDraftStore = () => {
    const inner = undoable(emptyDraftState, (state) => ({
        dirty: state.dirty,
        image: state.image,
        timestampInfo: structuredClone(state.timestampInfo),
        labels: Object.assign(Object.assign({}, structuredClone(state.labels)), { masks: state.labels.masks }),
        drawing: Object.assign(Object.assign({}, state.drawing), { active: state.drawing.active
                ? state.drawing.mode === "masks"
                    ? {
                        region: Object.assign(Object.assign({}, structuredClone(Object.assign(Object.assign({}, state.drawing.active.region), { map: undefined }))), { map: state.drawing.active.region.map }),
                        editable: state.drawing.active.editable,
                    }
                    : structuredClone(state.drawing.active)
                : undefined }),
    }), undefined, deallocateMaps);
    const reset = (labels, timestampInfo) => {
        const initial = get(inner.state);
        if (initial.image) {
            initial.image.free();
        }
        inner.state.reset(Object.assign(Object.assign({}, initial), { dirty: false, image: null, labels: labels2draft(labels), timestampInfo }));
    };
    return {
        history: inner.history,
        draft: Object.assign(Object.assign({}, inner.state), { reset, export: (dimensions) => (Object.assign(Object.assign({}, draft2labels(get(inner.state).labels)), { dimensions })) }),
    };
};
export const labels4timestamp = (labels, timestamp) => {
    if (!labels)
        return {
            label: { timestamp, end: undefined, labels: { image: {} } },
            exists: false,
        };
    const existing = labels.filter((l) => l.timestamp === timestamp)[0];
    return {
        label: existing || {
            timestamp,
            end: undefined,
            labels: { image: {} },
        },
        exists: !!existing,
    };
};
