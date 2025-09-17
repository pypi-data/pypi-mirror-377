import { SvelteComponent } from "svelte";
import type { Config, Labels, WidgetActions, ArbitraryMetadata, ImageStackTarget } from "../library/types.js";
declare const __propDef: {
    props: {
        target: ImageStackTarget | undefined;
        config: Config;
        labels: Labels;
        metadata?: ArbitraryMetadata;
        navigation?: boolean;
        editableConfig?: boolean;
        maxCanvasSize?: number;
        transitioning?: boolean;
        viewHeight?: number;
        actions?: WidgetActions;
    };
    events: {
        next: CustomEvent<any>;
        prev: CustomEvent<any>;
        delete: CustomEvent<any>;
        ignore: CustomEvent<any>;
        unignore: CustomEvent<any>;
        showIndex: CustomEvent<any>;
        save: CustomEvent<any>;
    } & {
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
