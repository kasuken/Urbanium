using MudBlazor.Services;
using Urbanium.Web.AI;
using Urbanium.Web.Components;
using Urbanium.Web.Engine;
using Urbanium.Web.Metrics;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

// Add MudBlazor services
builder.Services.AddMudServices();

// Add AI configuration
builder.Services.Configure<AIConfiguration>(
    builder.Configuration.GetSection(AIConfiguration.SectionName));

// Add Urbanium services
builder.Services.AddSingleton<WorldEngine>();
builder.Services.AddSingleton<MetricsService>();
builder.Services.AddSingleton<CitizenAIService>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}
app.UseStatusCodePagesWithReExecute("/not-found", createScopeForStatusCodePages: true);
app.UseHttpsRedirection();

app.UseAntiforgery();

app.MapStaticAssets();
app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();

app.Run();
