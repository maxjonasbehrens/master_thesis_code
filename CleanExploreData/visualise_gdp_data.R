
# Data Visualisation and Exploration --------------------------------------

library(dplyr)
library(ggplot2)  

# Load Data
library(readr)
enhanced_gdp_data <- read_csv("~/Documents/Msc/Thesis/Data/gdp_data/enhanced_gdp_data.csv")

dat <- enhanced_gdp_data

# Basic data manipulation
dat$nuts2 <- as.factor(dat$nuts2)
dat$year <- as.factor(dat$year)
dat$code <- as.factor(dat$code)
dat$country <- as.factor(dat$country)


# Basic Data Exploration --------------------------------------------------

dat[dat$country_value == max(dat$country_value),]

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
  ggplot(aes(reorder(country,-country_value),country_value))+
  geom_col()+
  theme_bw(base_size = 14)+
  xlab("Country")+
  ylab("Average GDP Value per country")+
  theme(axis.text.x = element_text(angle = 70, vjust = 1, hjust = 1))

