import { SvelteComponent } from "svelte";
import type { ImageStackTarget } from "../library/types.js";
declare const __propDef: {
    props: {
        stack: ImageStackTarget;
        selected?: number[];
        element?: HTMLImageElement | undefined;
    };
    events: {
        load: CustomEvent<any>;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type ImageStackProps = typeof __propDef.props;
export type ImageStackEvents = typeof __propDef.events;
export type ImageStackSlots = typeof __propDef.slots;
export default class ImageStack extends SvelteComponent<ImageStackProps, ImageStackEvents, ImageStackSlots> {
}
export {};
