import type { WidgetState, ForceableWritable } from "./library/types.js";
import Widget from "./components/Widget.svelte";
declare const defaultWidgetState: WidgetState;
declare const buildAttributeStoreFactory: <WidgetModelState extends {
    [key: string]: any;
}, T extends keyof WidgetModelState & string>(initializer: (name: T, set: (value: WidgetModelState[T] | null) => void) => {
    set: (value: WidgetModelState[T] | null) => void;
    destroy: () => void;
}) => {
    extract: (name: T) => ForceableWritable<WidgetModelState[T] | null>;
    destroy: () => void;
};
export default Widget;
export { buildAttributeStoreFactory, defaultWidgetState };
