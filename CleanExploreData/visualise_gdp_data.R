
# Data Visualisation and Exploration --------------------------------------

library(dplyr)
library(ggplot2)  

# Load Data
library(readr)
enhanced_gdp_data <- read_csv("~/Documents/Msc/Thesis/Data/gdp_data/enhanced_gdp_data.csv")

dat <- enhanced_gdp_data

# Basic data manipulation
dat$nuts2 <- as.factor(dat$nuts2)
#dat$year <- as.factor(dat$year)
dat$code <- as.factor(dat$code)
dat$country <- as.factor(dat$country)

# Available data
nrow(dat[dat$year>2014,])

# Basic Data Exploration --------------------------------------------------

# Region with highest value
dat[dat$country_value == max(dat$country_value),]

# No. of regions per country
country_count <- dat %>% 
  group_by(country) %>% 
  summarise(distinct_regions = n_distinct(nuts2)) %>% 
  arrange(desc(distinct_regions))

stargazer::stargazer(country_count, summary = FALSE)

country_count
sum(country_count$distinct_regions)

dat %>% 
  group_by(year) %>% 
  summarise(distinct_regions = n_distinct(nuts2)) %>% 
  arrange(desc(distinct_regions))

# Visualisation -----------------------------------------------------------

# Course of country mean over time
dat %>% 
  ggplot(aes(year, country_value, color = country, group = country))+
  geom_line()+
  theme_bw()

# Mean Country Value as Barplot
dat %>% 
  group_by(country) %>% 
  summarise(country_value = mean(country_value)) %>% 
  ggplot(aes(reorder(country,-country_value),country_value, fill = country_value))+
  geom_col()+
  theme_bw(base_size = 14)+
  xlab("Country")+
  ylab("Average GDP Value per country")+
  theme(axis.text.x = element_text(angle = 70, vjust = 1, hjust = 1))+
  theme(legend.position = "none")

ggsave("mean_gdp_per_country.png", width = 8, height = 6)
