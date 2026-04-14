import type { Event } from "@opencode-ai/sdk";
import type { Context } from "grammy";
import type { UserSession } from "./opencode.types.js";

import messageUpdated from "./event-handlers/message.updated.handler.js";
import messageRemoved from "./event-handlers/message.removed.handler.js";
import sessionStatus from "./event-handlers/session.status.handler.js";
import sessionIdle from "./event-handlers/session.idle.handler.js";
import sessionError from "./event-handlers/session.error.handler.js";
import fileEdited from "./event-handlers/file.edited.handler.js";
import ptyCreated from "./event-handlers/pty.created.handler.js";
import ptyExited from "./event-handlers/pty.exited.handler.js";
import serverInstanceDisposed from "./event-handlers/server.instance.disposed.handler.js";
import installationUpdated from "./event-handlers/installation.updated.handler.js";
import installationUpdateAvailable from "./event-handlers/installation.update-available.handler.js";
import lspClientDiagnostics from "./event-handlers/lsp.client.diagnostics.handler.js";
import lspUpdated from "./event-handlers/lsp.updated.handler.js";
import messagePartUpdated from "./event-handlers/message.part.updated.handler.js";
import messagePartRemoved from "./event-handlers/message.part.removed.handler.js";
import permissionUpdated from "./event-handlers/permission.updated.handler.js";
import permissionReplied from "./event-handlers/permission.replied.handler.js";
import sessionCompacted from "./event-handlers/session.compacted.handler.js";
import todoUpdated from "./event-handlers/todo.updated.handler.js";
import commandExecuted from "./event-handlers/command.executed.handler.js";
import sessionCreated from "./event-handlers/session.created.handler.js";
import sessionUpdated from "./event-handlers/session.updated.handler.js";
import sessionDeleted from "./event-handlers/session.deleted.handler.js";
import sessionDiff from "./event-handlers/session.diff.handler.js";
import fileWatcherUpdated from "./event-handlers/file.watcher.updated.handler.js";
import vcsBranchUpdated from "./event-handlers/vcs.branch.updated.handler.js";
import tuiPromptAppend from "./event-handlers/tui.prompt.append.handler.js";
import tuiCommandExecute from "./event-handlers/tui.command.execute.handler.js";
import tuiToastShow from "./event-handlers/tui.toast.show.handler.js";
import ptyUpdated from "./event-handlers/pty.updated.handler.js";
import ptyDeleted from "./event-handlers/pty.deleted.handler.js";
import serverConnected from "./event-handlers/server.connected.handler.js";
import { escapeHtml } from "./event-handlers/utils.js";

/**
 * Handler function signature for processing events
 * Returns a message string to send to the user, or null to ignore the event
 */
type EventHandlerFn<T extends Event> = (
    event: T,
    ctx: Context,
    userSession: UserSession
) => Promise<string | null>;

/**
 * Strongly-typed map of event handlers
 * Keys must be valid event types from the Event union
 * Values are handler functions that receive the specific event type
 */
type EventHandlerMap = {
    [K in Event["type"]]?: EventHandlerFn<Extract<Event, { type: K }>>;
};

/**
 * Event handler rules
 * Add or modify handlers for specific event types here
 */
export const eventHandlers: EventHandlerMap = {
    "message.updated": messageUpdated,
    "message.removed": messageRemoved,
    "message.part.updated": messagePartUpdated,
    "message.part.removed": messagePartRemoved,
    "permission.updated": permissionUpdated,
    "permission.replied": permissionReplied,
    "session.status": sessionStatus,
    "session.idle": sessionIdle,
    "session.compacted": sessionCompacted,
    "session.error": sessionError,
    "session.created": sessionCreated,
    "session.updated": sessionUpdated,
    "session.deleted": sessionDeleted,
    "session.diff": sessionDiff,
    "file.edited": fileEdited,
    "file.watcher.updated": fileWatcherUpdated,
    "todo.updated": todoUpdated,
    "command.executed": commandExecuted,
    "vcs.branch.updated": vcsBranchUpdated,

    "installation.updated": installationUpdated,
    "installation.update-available": installationUpdateAvailable,
    "lsp.client.diagnostics": lspClientDiagnostics,
    "lsp.updated": lspUpdated,

    "tui.prompt.append": tuiPromptAppend,
    "tui.command.execute": tuiCommandExecute,
    "tui.toast.show": tuiToastShow,

    "pty.created": ptyCreated,
    "pty.updated": ptyUpdated,
    "pty.exited": ptyExited,
    "pty.deleted": ptyDeleted,

    "server.instance.disposed": serverInstanceDisposed,
    "server.connected": serverConnected,
};

/**
 * Default handler for events that don't have a specific handler
 * Formats the event with its type and properties
 */
async function defaultHandler(event: Event, ctx: Context, userSession: UserSession): Promise<string> {
    const eventType = event.type;
    const properties = event.properties || {};

    const propsStr = JSON.stringify(properties, null, 2);
    return `🔔 <b>Event:</b> ${escapeHtml(eventType)}\n<pre>${escapeHtml(propsStr)}</pre>`;
}

/**
 * Process an event through the appropriate handler
 * Returns a message to send to the user, or null to ignore the event
 */
export async function processEvent(
    event: Event,
    ctx: Context,
    userSession: UserSession
): Promise<string | null> {
    try {
        // Check if we have a specific handler for this event type
        const handler = eventHandlers[event.type];

        if (handler) {
            // TypeScript knows the event type is correct here
            const result = await handler(event as any, ctx, userSession);
            if (result) {
                // console.log(`[EventHandler] Handled event: ${event.type}`);
                return result;
            }
        }

        if (!handler) {
            return null
        }
    } catch (error) {
        console.error(`Error handling event ${event.type}:`, error);
        return null;
    }
}
