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
export type ImageLabelerProps = typeof __propDef.props;
export type ImageLabelerEvents = typeof __propDef.events;
export type ImageLabelerSlots = typeof __propDef.slots;
export default class ImageLabeler extends SvelteComponent<ImageLabelerProps, ImageLabelerEvents, ImageLabelerSlots> {
}
export {};
