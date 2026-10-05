export type Platform = "meta" | "google";

export type ValidationIssue = {
  field: string;
  maximum: number;
  actual: number;
  message: string;
};

export type CampaignCopy = {
  primary_text?: string;
  headline?: string;
  description?: string;
  cta?: string;
  google_headlines?: string[];
  google_descriptions?: string[];
};

export type CampaignVariant = {
  angle: string;
  copy: CampaignCopy;
  creative_brief: string;
  validation_issues: ValidationIssue[];
};

export type CampaignDraftData = {
  draft_id: string;
  status: string;
  budget: string;
  variants: Partial<Record<Platform, CampaignVariant[]>>;
};

export type CampaignDraftInput = {
  offer_name: string;
  benefit: string;
  audience: string;
  proof: string;
  cta: string;
  price: string;
  gross_margin_pct: string;
  checkout_conversion_pct: string;
  refund_pct: string;
  currency: string;
  budget: string;
  platforms: Platform[];
};

export type OperationPreview = {
  operation_id: string;
  token: string;
  expires_at: string;
  payload_hash: string;
  summary: string;
  status: string;
};

export type OperationResult = {
  operation_id: string;
  status: string;
  campaign: { provider_id: string; platform: Platform; status: string };
};
