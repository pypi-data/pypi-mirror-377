import { SvelteComponent } from "svelte";
declare const __propDef: {
    props: {
        disabled: boolean;
        dataIndex: number;
        basis: string;
        text: string;
        className?: string | null;
        tooltip?: string | null;
        highlighted?: boolean;
    };
    events: {
        click: PointerEvent;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type ButtonProps = typeof __propDef.props;
export type ButtonEvents = typeof __propDef.events;
export type ButtonSlots = typeof __propDef.slots;
export default class Button extends SvelteComponent<ButtonProps, ButtonEvents, ButtonSlots> {
}
export {};
