import { SvelteComponent } from "svelte";
import type { ButtonConfig } from '../library/types.js';
declare const __propDef: {
    props: {
        configs: ButtonConfig[];
    };
    events: {
        click: CustomEvent<any>;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type ButtonGroupProps = typeof __propDef.props;
export type ButtonGroupEvents = typeof __propDef.events;
export type ButtonGroupSlots = typeof __propDef.slots;
export default class ButtonGroup extends SvelteComponent<ButtonGroupProps, ButtonGroupEvents, ButtonGroupSlots> {
}
export {};
