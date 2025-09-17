import { SvelteComponent } from "svelte";
declare const __propDef: {
    props: {
        images: string[];
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type ImagePreloaderProps = typeof __propDef.props;
export type ImagePreloaderEvents = typeof __propDef.events;
export type ImagePreloaderSlots = typeof __propDef.slots;
export default class ImagePreloader extends SvelteComponent<ImagePreloaderProps, ImagePreloaderEvents, ImagePreloaderSlots> {
}
export {};
