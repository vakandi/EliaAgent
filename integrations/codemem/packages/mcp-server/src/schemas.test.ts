import { REMEMBER_MEMORY_KINDS } from "@codemem/core";
import { describe, expect, it } from "vitest";
import { memoryKindSchema } from "./schemas.js";

describe("memoryKindSchema", () => {
	it("accepts every remember kind from the core catalog", () => {
		for (const kind of REMEMBER_MEMORY_KINDS) {
			expect(memoryKindSchema.safeParse(kind).success).toBe(true);
		}
	});

	it("rejects session_summary and unknown kinds", () => {
		expect(memoryKindSchema.safeParse("session_summary").success).toBe(false);
		expect(memoryKindSchema.safeParse("not-a-kind").success).toBe(false);
	});
});
