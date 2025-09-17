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
export type MediaIndexProps = typeof __propDef.props;
export type MediaIndexEvents = typeof __propDef.events;
export type MediaIndexSlots = typeof __propDef.slots;
export default class MediaIndex extends SvelteComponent<MediaIndexProps, MediaIndexEvents, MediaIndexSlots> {
}
export {};
