import { SvelteComponent } from "svelte";
import type { ArbitraryMetadata } from "../library/types.js";
declare const __propDef: {
    props: {
        metadata?: ArbitraryMetadata | undefined;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type MetadataProps = typeof __propDef.props;
export type MetadataEvents = typeof __propDef.events;
export type MetadataSlots = typeof __propDef.slots;
export default class Metadata extends SvelteComponent<MetadataProps, MetadataEvents, MetadataSlots> {
}
export {};
