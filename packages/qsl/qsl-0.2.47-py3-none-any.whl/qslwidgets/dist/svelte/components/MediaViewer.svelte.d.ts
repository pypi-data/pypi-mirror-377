import { SvelteComponent } from "svelte";
import type { Dimensions, MediaLoadState } from "../library/types.js";
declare const __propDef: {
    props: {
        size: Dimensions | undefined;
        viewHeight?: number | null;
        fixedHeight?: boolean;
        loadState?: MediaLoadState;
        enhancementControls?: boolean;
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        main: {};
        regions: {};
        mini: {};
        'custom-controls': {};
    };
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type MediaViewerProps = typeof __propDef.props;
export type MediaViewerEvents = typeof __propDef.events;
export type MediaViewerSlots = typeof __propDef.slots;
export default class MediaViewer extends SvelteComponent<MediaViewerProps, MediaViewerEvents, MediaViewerSlots> {
}
export {};
