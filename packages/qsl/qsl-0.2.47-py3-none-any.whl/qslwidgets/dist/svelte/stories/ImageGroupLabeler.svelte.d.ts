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
export type ImageGroupLabelerProps = typeof __propDef.props;
export type ImageGroupLabelerEvents = typeof __propDef.events;
export type ImageGroupLabelerSlots = typeof __propDef.slots;
export default class ImageGroupLabeler extends SvelteComponent<ImageGroupLabelerProps, ImageGroupLabelerEvents, ImageGroupLabelerSlots> {
}
export {};
