import { SvelteComponent } from "svelte";
declare const __propDef: {
    props: Record<string, never>;
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type BatchImageLabelerProps = typeof __propDef.props;
export type BatchImageLabelerEvents = typeof __propDef.events;
export type BatchImageLabelerSlots = typeof __propDef.slots;
export default class BatchImageLabeler extends SvelteComponent<BatchImageLabelerProps, BatchImageLabelerEvents, BatchImageLabelerSlots> {
}
export {};
