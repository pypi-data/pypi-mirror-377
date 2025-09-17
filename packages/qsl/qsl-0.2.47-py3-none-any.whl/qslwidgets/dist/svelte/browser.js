import Widget, { defaultWidgetState, buildAttributeStoreFactory, } from "./widget";
const buildModelStateExtractor = (state) => {
    return buildAttributeStoreFactory((name, set) => {
        console.log(`Initializing ${name} to ${state[name]}`);
        set(state[name]);
        return {
            set: (value) => console.log(`Changing ${name} to ${value}.`),
            destroy: () => null
        };
    });
};
const createLabelerInterface = (target) => {
    return new Widget({
        target: target,
        props: { extract: buildModelStateExtractor(defaultWidgetState).extract },
    });
};
export { createLabelerInterface };
