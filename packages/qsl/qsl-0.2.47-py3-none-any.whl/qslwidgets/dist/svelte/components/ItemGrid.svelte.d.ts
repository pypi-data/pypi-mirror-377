import { SvelteComponent } from "svelte";
declare const __propDef: {
    props: {
        itemSize?: number;
        itemGap?: number;
    };
    events: {
        click: PointerEvent;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        default: {};
    };
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type ItemGridProps = typeof __propDef.props;
export type ItemGridEvents = typeof __propDef.events;
export type ItemGridSlots = typeof __propDef.slots;
export default class ItemGrid extends SvelteComponent<ItemGridProps, ItemGridEvents, ItemGridSlots> {
}
export {};
