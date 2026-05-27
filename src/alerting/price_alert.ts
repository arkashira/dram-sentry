import { retry, ApiError } from '@/utils/api_retry';
import { fetchSupplierPrices } from '@/services/price_fetcher';
import { sendAlert } from '@/services/alert_dispatcher';

/** Configuration (externalize in production) */
const PRICE_CHANGE_THRESHOLD_PERCENT = 5;
const RETRY_OPTIONS = {
  maxAttempts: 4,
  baseDelayMs: 800,
  maxDelayMs: 10_000,
  jitterFactor: 0.1,
  onRetry: (err: unknown, attempt: number, delayMs: number) => {
    console.warn(`[price_alert] Retry ${attempt}/${RETRY_OPTIONS.maxAttempts} in ${delayMs}ms. Error:`, err);
  },
  shouldRetry: (err: unknown) => {
    // Retry on transient errors (5xx, 429, timeouts) but fail fast on auth/validation errors.
    if (err instanceof ApiError) return err.retryable;
    if (err instanceof Error) {
      return err.message.includes('ECONNRESET') ||
             err.message.includes('ETIMEDOUT') ||
             (err as any).status >= 500;
    }
    return true;
  },
};

interface SupplierPrice {
  supplier: string;
  priceUsdPerGb: number;
  timestamp: number;
}

const latestPrices = new Map<string, SupplierPrice>();

function evaluateAndAlert(prices: SupplierPrice[]): void {
  for (const price of prices) {
    const previous = latestPrices.get(price.supplier);
    if (previous) {
      const changePct = ((price.priceUsdPerGb - previous.priceUsdPerGb) / previous.priceUsdPerGb) * 100;
      if (Math.abs(changePct) >= PRICE_CHANGE_THRESHOLD_PERCENT) {
        const alertMessage = `Price change for ${price.supplier}: ${previous.priceUsdPerGb.toFixed(2)} → ${price.priceUsdPerGb.toFixed(2)} USD/GB (${changePct.toFixed(1)}%)`;
        console.info(`[price_alert] Triggering alert: ${alertMessage}`);
        sendAlert({
          title: 'DRAM Spot Price Alert',
          message: alertMessage,
          severity: 'warning',
          metadata: { supplier: price.supplier, changePct },
        });
      }
    }
    latestPrices.set(price.supplier, price);
  }
}

export async function processPriceAlerts(): Promise<void> {
  try {
    const prices = await retry<SupplierPrice[]>(fetchSupplierPrices, RETRY_OPTIONS);
    evaluateAndAlert(prices);
  } catch (err) {
    const apiError = err instanceof ApiError
      ? err
      : new ApiError('Failed to fetch supplier prices', err, false);
    console.error('[price_alert] Critical error:', apiError);
    // Optionally: Push to dead-letter queue or monitoring system.
  }
}