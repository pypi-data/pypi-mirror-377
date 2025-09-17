import { SvelteComponent } from "svelte";
import type { LabelConfig } from '../library/types.js';
declare const __propDef: {
    props: {
        open: boolean;
        existing?: {
            level: "image" | "regions";
            config: LabelConfig;
        } | undefined;
    };
    events: {
        save: CustomEvent<any>;
        close: CustomEvent<any>;
    } & {
        [evt: string]: CustomEvent<any>;
    };
    slots: {};
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type ConfigEditorProps = typeof __propDef.props;
export type ConfigEditorEvents = typeof __propDef.events;
export type ConfigEditorSlots = typeof __propDef.slots;
export default class ConfigEditor extends SvelteComponent<ConfigEditorProps, ConfigEditorEvents, ConfigEditorSlots> {
}
export {};
