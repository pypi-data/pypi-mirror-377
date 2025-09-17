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
export type ImageStackLabelerProps = typeof __propDef.props;
export type ImageStackLabelerEvents = typeof __propDef.events;
export type ImageStackLabelerSlots = typeof __propDef.slots;
export default class ImageStackLabeler extends SvelteComponent<ImageStackLabelerProps, ImageStackLabelerEvents, ImageStackLabelerSlots> {
}
export {};
