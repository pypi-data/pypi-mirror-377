import { SvelteComponent } from "svelte";
declare const __propDef: {
    props: Record<string, never>;
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        default: {};
    };
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type EnhancementControlsProps = typeof __propDef.props;
export type EnhancementControlsEvents = typeof __propDef.events;
export type EnhancementControlsSlots = typeof __propDef.slots;
export default class EnhancementControls extends SvelteComponent<EnhancementControlsProps, EnhancementControlsEvents, EnhancementControlsSlots> {
}
export {};
