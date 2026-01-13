export interface ConversionResponse {
  success: boolean;
  message: string;
  download_url?: string;
  file_size?: number;
  original_filename?: string;
  title?: string;
}

export interface SupportedFormat {
  supported_formats: string[];
  conversions: {
    from: string;
    to: string;
    description: string;
  }[];
}

export interface ConversionRequest {
  file: File;
  target_format: string;
  title?: string;
  author?: string;
}