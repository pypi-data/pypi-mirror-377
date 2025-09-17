import { getContext } from "svelte";
import { writable } from "svelte/store";
import { v4 as uuidv4 } from "uuid";
const createEnhancements = () => {
    return writable({
        brightness: 1,
        saturation: 1,
        contrast: 1,
    });
};
const createToast = () => {
    const { subscribe, update } = writable([]);
    let count = 0;
    const push = (msg, opts = {}) => {
        const entry = Object.assign(Object.assign({ duration: 4000, initial: 1, next: 0, pausable: false, dismissable: true, classes: [], theme: {}, reversed: false, intro: { x: 256 }, msg }, opts), { id: ++count });
        update((n) => (entry.reversed ? [...n, entry] : [entry, ...n]));
        return count;
    };
    const pop = (id) => {
        update((n) => {
            if (!n.length || id === 0)
                return [];
            return n.filter((i) => i.id !== id);
        });
    };
    return { subscribe, push, pop };
};
export const createStores = () => ({
    toast: createToast(),
    enhancements: createEnhancements(),
    id: uuidv4(),
});
export const getStores = () => getContext("sharedStores");
