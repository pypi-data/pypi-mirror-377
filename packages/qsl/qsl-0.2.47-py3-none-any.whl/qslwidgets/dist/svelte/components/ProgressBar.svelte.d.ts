import { SvelteComponent } from "svelte";
declare const __propDef: {
    props: {
        progress: number;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type ProgressBarProps = typeof __propDef.props;
export type ProgressBarEvents = typeof __propDef.events;
export type ProgressBarSlots = typeof __propDef.slots;
export default class ProgressBar extends SvelteComponent<ProgressBarProps, ProgressBarEvents, ProgressBarSlots> {
}
export {};
