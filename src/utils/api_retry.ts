import { setTimeout } from 'timers/promises';

/**
 * Retry configuration with exponential backoff, jitter, and circuit-breaking.
 * Inspired by Python's `tenacity` and AWS SDK retry strategies.
 */
export interface RetryOptions {
  /** Maximum number of attempts (including initial call). Default: 3 */
  maxAttempts?: number;
  /** Base delay in milliseconds for exponential backoff. Default: 1000 */
  baseDelayMs?: number;
  /** Maximum delay between retries (cap exponential growth). Default: 30_000 */
  maxDelayMs?: number;
  /** Jitter factor (0-1) to avoid thundering herd. Default: 0.2 */
  jitterFactor?: number;
  /** Optional callback invoked before each retry (except first attempt). */
  onRetry?: (error: unknown, attempt: number, delayMs: number) => void;
  /** Stop retrying if this predicate returns false. Default: retry all errors. */
  shouldRetry?: (error: unknown) => boolean;
}

/**
 * Custom error hierarchy for API failures.
 */
export class ApiError extends Error {
  public readonly originalError: unknown;
  public readonly retryable: boolean;

  constructor(
    message: string,
    originalError: unknown,
    retryable: boolean = true,
  ) {
    super(message);
    this.name = 'ApiError';
    this.originalError = originalError;
    this.retryable = retryable;
    if (Error.captureStackTrace) Error.captureStackTrace(this, ApiError);
  }
}

/**
 * Retries a promise-returning function with exponential backoff + jitter.
 * Throws `ApiError` (with `retryable` flag) after exhausting attempts.
 */
export async function retry<T>(
  fn: () => Promise<T>,
  opts: RetryOptions = {},
): Promise<T> {
  const {
    maxAttempts = 3,
    baseDelayMs = 1000,
    maxDelayMs = 30_000,
    jitterFactor = 0.2,
    onRetry,
    shouldRetry = () => true,
  } = opts;

  let lastError: unknown;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (err) {
      lastError = err;
      if (!shouldRetry(err)) break;

      if (attempt < maxAttempts) {
        const delayMs = Math.min(
          maxDelayMs,
          baseDelayMs * Math.pow(2, attempt - 1) * (1 + Math.random() * jitterFactor),
        );
        if (onRetry) {
          try {
            onRetry(err, attempt, delayMs);
          } catch (_) { /* Swallow callback errors */ }
        }
        await setTimeout(delayMs);
      }
    }
  }
  throw new ApiError(
    `Failed after ${maxAttempts} attempts`,
    lastError,
    lastError instanceof ApiError ? lastError.retryable : true,
  );
}