                    for component in missing_components:
                        logger.info(f"Attempting to generate missing {component}")
                        generated_component = self._generate_missing_component(component, outfit_data)
                        if generated_component and not generated_component.startswith("Please provide"):
                            outfit_data[component] = generated_component
                        else:
                            logger.error(f"Failed to generate valid {component}")
                            break
                    
                    retries += 1
                
                if retries == max_retries:
                    logger.error(f"Failed to generate valid outfit after {max_retries} attempts")
        
        return outfits 