// Sample TypeScript module for the capability-index fixture.
export function rankCandidates(rows: Row[]): Row[] {
  return rows;
}

export const DEFAULT_THRESHOLD = 2;

export class CandidateStore {}

function internalOnly() {}

export { internalOnly as exposedHelper };
