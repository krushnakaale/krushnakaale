# Configuration

Edit [profile.yml](../config/profile.yml) for data generation.

| Key | Meaning |
| --- | --- |
| username | GitHub account to fetch. For another account, also update the static README links, banner text and snake workflow username. |
| sort | recently_pushed, most_starred, alphabetical or recently_created. Ties use repository names. |
| repository_limit | Number of recent cards, from 1 to 50. |
| include_forks | Set true to include public forks. Archived repositories and the profile repository are always excluded. |
| exclude_repositories | Additional repository names to omit, matched without case sensitivity. |
| featured_repositories | Ordered list of verified repositories. Missing or ineligible selections are reported to workflow logs. |
| currently_working_on | Projects you confirm are in progress. An empty list hides this group. |
| learning_interests | Topics to display under Current focus. |

Edit the README and template for static skills, social links and prose. The refresh runs twice hourly and the snake runs daily. Edit the workflow cron rules to change those schedules. GitHub may delay scheduled jobs.
