import { SvelteComponent } from "svelte";
import type { Labels, Config, WidgetActions, ImageGroupTarget, ArbitraryMetadata } from "../library/types.js";
declare const __propDef: {
    props: {
        labels: Labels;
        config: Config;
        target?: ImageGroupTarget | undefined;
        navigation?: boolean;
        editableConfig?: boolean;
        transitioning?: boolean;
        metadata?: ArbitraryMetadata | undefined;
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
export type ImageGroupLabelerProps = typeof __propDef.props;
export type ImageGroupLabelerEvents = typeof __propDef.events;
export type ImageGroupLabelerSlots = typeof __propDef.slots;
export default class ImageGroupLabeler extends SvelteComponent<ImageGroupLabelerProps, ImageGroupLabelerEvents, ImageGroupLabelerSlots> {
}
export {};
