import { SvelteComponent } from "svelte";
declare const __propDef: {
    props: {
        layout?: "horizontal" | "vertical";
    };
    events: {
        [evt: string]: CustomEvent<any>;
    };
    slots: {
        content: {};
        control: {};
    };
    exports?: {} | undefined;
    bindings?: string | undefined;
};
export type LabelerLayoutProps = typeof __propDef.props;
export type LabelerLayoutEvents = typeof __propDef.events;
export type LabelerLayoutSlots = typeof __propDef.slots;
export default class LabelerLayout extends SvelteComponent<LabelerLayoutProps, LabelerLayoutEvents, LabelerLayoutSlots> {
}
export {};
