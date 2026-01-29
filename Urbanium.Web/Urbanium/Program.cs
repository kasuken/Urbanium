using Urbanium.Components;
using MudBlazor.Services;
using Urbanium.Configuration;
using Urbanium.Services;

var builder = WebApplication.CreateBuilder(args);

// Configure LM Studio settings
builder.Services.Configure<LMStudioSettings>(
    builder.Configuration.GetSection("LMStudio"));

// Configure Simulation settings
builder.Services.Configure<SimulationSettings>(
    builder.Configuration.GetSection("Simulation"));

// Register AI services
builder.Services.AddSingleton<MayorAgentService>();
builder.Services.AddSingleton<CitizenDecisionService>();
builder.Services.AddSingleton<CitizenAIEngine>();

// Register city services
builder.Services.AddSingleton<CityTimeService>();
builder.Services.AddSingleton<CitySimulationService>();

builder.Services.AddMudServices();

// Add services to the container.
builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

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