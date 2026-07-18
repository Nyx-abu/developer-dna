import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

def setup_telemetry():
    """Configure OpenTelemetry tracing and metrics."""
    resource = Resource.create({"service.name": "devdna-backend"})
    
    # QA feedback fix 3: Use proper env var instead of hardcoded localhost fallback
    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4318")
    
    # Tracing
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)
    span_exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces")
    span_processor = BatchSpanProcessor(span_exporter)
    tracer_provider.add_span_processor(span_processor)
    
    # QA feedback fix 2: Add metrics instrumentation (MeterProvider)
    metric_exporter = OTLPMetricExporter(endpoint=f"{otlp_endpoint}/v1/metrics")
    metric_reader = PeriodicExportingMetricReader(metric_exporter)
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # Instrument Django and Psycopg2
    # Ensure this is safe to run multiple times or skip if already instrumented
    if not hasattr(DjangoInstrumentor(), "_is_instrumented_by_opentelemetry") or not DjangoInstrumentor()._is_instrumented_by_opentelemetry:
        DjangoInstrumentor().instrument()
    if not hasattr(Psycopg2Instrumentor(), "_is_instrumented_by_opentelemetry") or not Psycopg2Instrumentor()._is_instrumented_by_opentelemetry:
        Psycopg2Instrumentor().instrument()
