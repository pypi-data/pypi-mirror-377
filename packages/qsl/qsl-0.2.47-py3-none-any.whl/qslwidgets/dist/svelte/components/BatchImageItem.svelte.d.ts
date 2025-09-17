import { SvelteComponent } from "svelte";
import type { ArbitraryMetadata } from "../library/types.js";
declare const __propDef: {
    props: {
        src: string | undefined;
        size: number;
        rotation?: number;
        labeled?: boolean | string;
        selected?: boolean | undefined;
        ignored?: boolean;
        metadata?: ArbitraryMetadata | undefined;
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
export type BatchImageItemProps = typeof __propDef.props;
export type BatchImageItemEvents = typeof __propDef.events;
export type BatchImageItemSlots = typeof __propDef.slots;
export default class BatchImageItem extends SvelteComponent<BatchImageItemProps, BatchImageItemEvents, BatchImageItemSlots> {
}
export {};
