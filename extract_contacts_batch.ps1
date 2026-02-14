# LinkedIn Contact Extraction - Immediate Write-Through
# Extracts visible contacts from current browser snapshot

$contacts = @(
    @{
        Name = "Stephan de Laat"
        Title = "PT6A and JT15D European Regional Sales Manager"
        Company = "StandardAero"
        Location = ""
        URL = "https://www.linkedin.com/in/stephan-de-laat-994100122/"
        Intro = "PT6A and JT15D European Regional Sales Manager at StandardAero"
        RecentActivity = ""
        BusinessFocus = ""
    },
    @{
        Name = "Cindy Francis"
        Title = "VP Engine Sales & BD-Americas"
        Company = ""
        Location = ""
        URL = "https://www.linkedin.com/in/cindy-francis-1a19108/"
        Intro = "VP Engine Sales & BD-Americas"
        RecentActivity = ""
        BusinessFocus = ""
    },
    @{
        Name = "Jakub Lenar"
        Title = "Aircraft Sales and Acquisitions Manager"
        Company = "JETRON"
        Location = ""
        URL = "https://www.linkedin.com/in/jakub-lenar-353486200/"
        Intro = "Aircraft Sales and Acquisitions Manager at JETRON"
        RecentActivity = ""
        BusinessFocus = ""
    },
    @{
        Name = "Nicholas Kattwinkel"
        Title = "Head of Sales | MRO Component Repair | Driving the Americas"
        Company = ""
        Location = ""
        URL = "https://www.linkedin.com/in/nicholas-kattwinkel/"
        Intro = "Head of Sales | MRO Component Repair | Driving the Americas"
        RecentActivity = ""
        BusinessFocus = ""
    },
    @{
        Name = "Byron Cruz"
        Title = "Materials Operations Manager"
        Company = "Spirit Airlines"
        Location = ""
        URL = "https://www.linkedin.com/in/byron-cruz-ab0170243/"
        Intro = "Materials Operations Manager at Spirit Airlines"
        RecentActivity = ""
        BusinessFocus = ""
    },
    @{
        Name = "Mahmoud Bashir"
        Title = "Chief Executive Officer"
        Company = "Jordan Airmotive (JALCo)"
        Location = ""
        URL = "https://www.linkedin.com/in/mahmoud-bashir-92997aba/"
        Intro = "Chief Executive Officer at Jordan Airmotive ( JALCo)"
        RecentActivity = ""
        BusinessFocus = ""
    },
    @{
        Name = "Marc Verspyck"
        Title = "Deputy CEO - Board Member"
        Company = ""
        Location = ""
        URL = "https://www.linkedin.com/in/marc-verspyck-761733/en/"
        Intro = "Deputy CEO - Board Member"
        RecentActivity = ""
        BusinessFocus = ""
    },
    @{
        Name = "François-xavier Rault"
        Title = "VP Sales APAC"
        Company = "AerFin"
        Location = ""
        URL = "https://www.linkedin.com/in/françois-xavier-rault/"
        Intro = "VP Sales APAC @ AerFin | Aftermarket | Airframe Component | Partnership"
        RecentActivity = ""
        BusinessFocus = ""
    },
    @{
        Name = "Aslihan Uçar"
        Title = "Director of Business Development- Turkiye&Middle East"
        Company = "Werner Aero, LLC"
        Location = ""
        URL = "https://www.linkedin.com/in/aslihan-uçar-14565532/"
        Intro = "Director of Business Development- Turkiye&Middle East at Werner Aero, LLC"
        RecentActivity = ""
        BusinessFocus = ""
    },
    @{
        Name = "Cheryll Mae Maata Silvestre"
        Title = "Sales & Business Development Representative"
        Company = "Werner Aero LLC"
        Location = ""
        URL = "https://www.linkedin.com/in/cheryll-mae-maata-silvestre-bb9020148/"
        Intro = "Sales & Business Development Representative At Werner Aero LLC"
        RecentActivity = ""
        BusinessFocus = ""
    }
)

$csvPath = "C:\Users\Haide\.openclaw\workspace\linkedin_connections_full.csv"

foreach ($contact in $contacts) {
    $row = [PSCustomObject]@{
        Name = $contact.Name
        Title = $contact.Title
        Company = $contact.Company
        Location = $contact.Location
        URL = $contact.URL
        Intro = $contact.Intro
        Recent_Activity_Summary = $contact.RecentActivity
        Business_Focus = $contact.BusinessFocus
    }
    
    $row | Export-Csv -Path $csvPath -Append -NoTypeInformation -Encoding UTF8
    Write-Host "✅ Wrote: $($contact.Name)"
}

Write-Host "`n🎯 Batch complete: 10 contacts added"
